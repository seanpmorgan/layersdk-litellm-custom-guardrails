"""
Simplified Layer SDK Custom Guardrail for LiteLLM
Focuses on basic functionality with Layer SDK bug workarounds
"""

import os
import re
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from litellm.integrations.custom_guardrail import CustomGuardrail

# Import Layer SDK components
from layer_sdk import layer, SessionActionKind, SessionActionError, OIDCClientCredentials

# Global deduplication to prevent duplicate processing across instances
_PROCESSED_RESPONSES = set()


class LayerGuardrail(CustomGuardrail):
    """Simplified guardrail that works around Layer SDK bugs"""
    
    def __init__(self, guardrail_name=None, **kwargs):
        super().__init__()
        self.guardrail_name = guardrail_name
        self.user_sessions = {}  # Store session IDs per user
        self.processed_requests = set()  # Prevent duplicate processing
        self.layer_initialized = False
        
        print(f"LayerGuardrail initialized (name: {guardrail_name})")
    
    def _ensure_layer_sdk_initialized(self):
        """Initialize Layer SDK"""
        if self.layer_initialized:
            return True
            
        try:
            # Try to create a test session to see if already initialized
            test_session = layer.create_session(attributes={"test": "init_check"})
            self.layer_initialized = True
            print("Layer SDK already initialized")
            return True
        except Exception as e:
            if "201" in str(e) and "session_id" in str(e):
                # Layer SDK is initialized but has the 201 bug
                self.layer_initialized = True
                print("Layer SDK initialized (with 201 bug)")
                return True
            else:
                # Need to initialize Layer SDK
                print(f"Initializing Layer SDK: {e}")
                return self._initialize_layer_sdk()

    def _initialize_layer_sdk(self):
        """Initialize Layer SDK with environment variables"""
        try:
            # Hardcoded values for testing (replace with your actual values)
            application_id = os.getenv("LAYER_APPLICATION_ID") or "42b1a5ce-584e-4c22-ba4d-080134599acc"
            base_url = os.getenv("LAYER_BASE_URL") or "https://layer.demo02.protectai.cloud/"
            environment = os.getenv("LAYER_ENVIRONMENT") or "demo02"
            
            # Load client secret from secrets.json as fallback
            client_secret = os.getenv("LAYER_OIDC_CLIENT_SECRET")
            if not client_secret:
                try:
                    with open('secrets.json') as f:
                        secrets = json.load(f)
                    client_secret = secrets.get('LAYER_DEMO2_AUTH_CLIENT_SECRET')
                except:
                    pass
            
            print(f"Initializing with app_id: {application_id}")
            
            # Initialize with authentication if available
            auth_provider = None
            client_id = os.getenv("LAYER_OIDC_CLIENT_ID") or "demo02/layer-sdk"
            if client_secret:
                auth_provider = OIDCClientCredentials(
                    token_url=os.getenv("LAYER_OIDC_TOKEN_URL", "https://auth.protectai.cloud/realms/demo02/protocol/openid-connect/token"),
                    client_id=client_id,
                    client_secret=client_secret,
                )
                print("Using OIDC authentication")
            
            layer.init(
                base_url=base_url,
                application_id=application_id,
                environment=environment,
                auth_provider=auth_provider,
                firewall_base_url=os.getenv("LAYER_FIREWALL_BASE_URL", "https://layer-firewall.demo02.protectai.cloud"),
                enable_firewall_instrumentation=True  # Enable firewall checking
            )
            
            self.layer_initialized = True
            print("Layer SDK initialized successfully in guardrail")
            return True
            
        except Exception as e:
            print(f"Failed to initialize Layer SDK: {e}")
            return False

    def _create_session_with_workaround(self, attributes):
        """Create session with workaround for Layer SDK bug"""
        try:
            return layer.create_session(attributes=attributes)
        except Exception as e:
            error_msg = str(e)
            if "201" in error_msg and "session_id" in error_msg:
                # Extract session ID from the "error" message
                match = re.search(r'"session_id":\s*"([^"]+)"', error_msg)
                if match:
                    session_id = match.group(1)
                    print(f"Extracted session_id from 201 'error': {session_id}")
                    return session_id
            raise e

    def _extract_user_id(self, data: dict, user_api_key_dict=None) -> str:
        print(f"\n=== USER_ID EXTRACTION DEBUG ===")
        
        user_id = None
        
        # 1. Check headers in metadata (this is where LiteLLM stores them)
        if 'metadata' in data and isinstance(data['metadata'], dict):
            metadata = data['metadata']
            if 'headers' in metadata and isinstance(metadata['headers'], dict):
                headers = metadata['headers']
                print(f"Found headers in metadata: {list(headers.keys())}")
                
                # Look for user ID headers (case insensitive)
                user_id = (headers.get('x-user-id') or 
                        headers.get('X-User-ID') or
                        headers.get('user-id') or
                        headers.get('User-ID'))
                
                if user_id:
                    print(f"Found user_id in metadata headers: {user_id}")
                    return str(user_id)
        
        # 2. Check request body for user field
        if data.get("user"):
            user_id = data.get("user")
            print(f"Found user_id in request body: {user_id}")
            return str(user_id)
        
        # 3. Fallback
        print(f"No user_id found, using default")
        return "default_user_id"

    async def async_pre_call_hook(self, user_api_key_dict, cache, data: dict, call_type: str, **kwargs) -> Optional[dict]:
        """Pre-call: Create/reuse session, track prompt, and enforce firewall policies"""
        # Create a unique request ID to prevent duplicate processing
        request_id = f"{id(data)}_{hash(str(data.get('messages', '')))}"
        
        if request_id in self.processed_requests:
            print(f"PRE_CALL: Skipping duplicate request {request_id}")
            return data
        
        self.processed_requests.add(request_id)
        print(f"PRE_CALL: Processing request {request_id}")
        
        if not self._ensure_layer_sdk_initialized():
            print("Layer SDK not available - skipping tracking")
            return data
            
        try:
            user_id = self._extract_user_id(data, user_api_key_dict)
            model_name = data.get("model", "unknown")
            
            print(f"User: {user_id}, Model: {model_name}")
            
            # Check if user has a blocked session that should not be reused
            if user_id in self.user_sessions:
                existing_session = self.user_sessions[user_id]
                if hasattr(self, 'blocked_sessions') and existing_session in self.blocked_sessions:
                    print(f"Previous session {existing_session} was blocked, creating new session for user {user_id}")
                    del self.user_sessions[user_id]
                else:
                    print(f"Reusing session: {existing_session}")
            
            # Get or create session
            if user_id in self.user_sessions:
                session_id = self.user_sessions[user_id]
                print(f"Reusing session: {session_id}")
            else:
                session_attributes = {
                    "user.id": user_id,
                    "model.name": model_name,
                    "source": "litellm-guardrail"
                }
                
                session_id = self._create_session_with_workaround(session_attributes)
                self.user_sessions[user_id] = session_id
                print(f"Created session: {session_id}")
            
            # Track prompt first
            messages = data.get("messages", [])
            try:
                layer.append_action(
                    session_id=session_id,
                    kind=SessionActionKind.COMPLETION_PROMPT,
                    start_time=datetime.now(timezone.utc),
                    end_time=datetime.now(timezone.utc),
                    attributes={"model.id": model_name},
                    data={"messages": messages}
                )
                print(f"Tracked prompt for session: {session_id}")
            except Exception as e:
                print(f"Failed to track prompt: {e}")
            
            # Check firewall after logging the prompt
            print(f"About to check firewall for session: {session_id}")
            try:
                firewall_response = layer.firewall_session_lookup(session_id)
                print(f"Firewall response: {firewall_response.decision}")
                print(f"Violated policies: {len(firewall_response.context.get('violated_policies', []))}")
                
                if firewall_response.decision.lower() == "block":
                    print(f"BLOCKING REQUEST AND SESSION - Session {session_id}")
                    
                    # Initialize blocked_sessions set if it doesn't exist
                    if not hasattr(self, 'blocked_sessions'):
                        self.blocked_sessions = set()
                    
                    # Mark session as blocked and remove from active sessions
                    self.blocked_sessions.add(session_id)
                    if user_id in self.user_sessions:
                        del self.user_sessions[user_id]
                        print(f"Removed blocked session {session_id} for user {user_id}")
                    
                    # Log session termination action
                    try:
                        layer.append_action(
                            session_id=session_id,
                            kind=SessionActionKind.COMPLETION_OUTPUT,
                            start_time=datetime.now(timezone.utc),
                            end_time=datetime.now(timezone.utc),
                            attributes={
                                "status": "session_blocked",
                                "block_reason": "firewall_policy_violation",
                                "user.id": user_id
                            },
                            data={
                                "action": "session_terminated_due_to_policy_violation",
                                "violated_policies": firewall_response.context.get('violated_policies', [])
                            }
                        )
                        print(f"Logged session termination for {session_id}")
                    except Exception as log_error:
                        print(f"Failed to log session termination: {log_error}")
                    
                    # Extract policy names for error message
                    policy_names = [p.get('name', 'Unknown') for p in firewall_response.context.get('violated_policies', [])]
                    raise Exception(f"Request blocked by firewall. Session terminated. Violated policies: {', '.join(policy_names)}")
                else:
                    print(f"Request allowed - Session {session_id}")
                    
            except Exception as firewall_error:
                if "blocked by firewall" in str(firewall_error).lower():
                    raise firewall_error
                else:
                    print(f"Firewall check failed: {firewall_error}")
            
            # Store session info for post-call (with request ID for matching)
            data['_layer_session_id'] = session_id
            data['_layer_user_id'] = user_id
            data['_layer_request_id'] = request_id
            
            return data
            
        except Exception as e:
            if "blocked by firewall" in str(e).lower():
                print(f"Request blocked: {e}")
                raise e  # This will cause LiteLLM to return an error to the client
            else:
                print(f"Error in pre_call_hook: {e}")
                return data
        
        
    async def async_post_call_success_hook(self, user_api_key_dict, response, call_type=None, **kwargs) -> dict:
        """Post-call: Track successful response"""
        global _PROCESSED_RESPONSES
        
        # Create unique identifier for this response
        response_id = getattr(response, 'id', None) or f"resp_{id(response)}"
        
        if response_id in _PROCESSED_RESPONSES:
            print(f"POST_CALL_SUCCESS: Skipping duplicate response {response_id}")
            return response
        
        _PROCESSED_RESPONSES.add(response_id)
        print(f"POST_CALL_SUCCESS: Processing response {response_id}")
        
        if not self.layer_initialized:
            return response
            
        try:
            # Get session info from request data
            request_data = kwargs.get('data', {})
            session_id = request_data.get('_layer_session_id')
            user_id = request_data.get('_layer_user_id', 'unknown')
            
            print(f"Found session: {session_id}, user: {user_id}")
            
            if session_id:
                # Extract response content
                content = ""
                if hasattr(response, 'choices') and response.choices:
                    content = response.choices[0].message.content or ""
                
                # Create a content-based unique key to prevent duplicate tracking
                content_hash = hash(content + str(response_id))
                content_key = f"content_{content_hash}"
                
                if content_key in _PROCESSED_RESPONSES:
                    print(f"Skipping duplicate content tracking for session: {session_id}")
                    return response
                
                _PROCESSED_RESPONSES.add(content_key)
                
                # Track response
                try:
                    layer.append_action(
                        session_id=session_id,
                        kind=SessionActionKind.COMPLETION_OUTPUT,
                        start_time=datetime.now(timezone.utc),
                        end_time=datetime.now(timezone.utc),
                        attributes={"model.id": request_data.get('model', 'unknown')},
                        data={"messages": [{"role": "assistant", "content": content}]}
                    )
                    print(f"Tracked response for session: {session_id}")
                except Exception as e:
                    print(f"Failed to track response: {e}")
            else:
                print("No session_id found in request data")
            
            return response
            
        except Exception as e:
            print(f"Error in post_call_success_hook: {e}")
            return response

    async def async_post_call_failure_hook(self, user_api_key_dict, original_exception, request_data=None, call_type=None, **kwargs):
        """Post-call failure: Track errors and firewall blocks"""
        if self.layer_initialized and self.user_sessions:
            try:
                session_id = list(self.user_sessions.values())[-1]
                
                # Check if this was a firewall block
                error_message = str(original_exception)
                is_firewall_block = "blocked by firewall" in error_message.lower()
                
                layer.append_action(
                    session_id=session_id,
                    kind=SessionActionKind.COMPLETION_OUTPUT,
                    start_time=datetime.now(timezone.utc),
                    end_time=datetime.now(timezone.utc),
                    attributes={
                        "status": "blocked" if is_firewall_block else "failed",
                        "block_reason": "firewall_policy" if is_firewall_block else "error",
                        "error_type": type(original_exception).__name__
                    },
                    error=SessionActionError(message=str(original_exception))
                )
                
                if is_firewall_block:
                    print(f"Tracked firewall block for session: {session_id}")
                else:
                    print(f"Tracked error for session: {session_id}")
                    
            except Exception as e:
                print(f"Failed to track error: {e}")
        
        raise original_exception


# Export the class
myCustomGuardrail = LayerGuardrail