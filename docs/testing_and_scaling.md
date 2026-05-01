# Testing, Validation, and Scaling

## Sample Validation Metrics
Use these for demo reporting after running `scripts/evaluate.py`:
- Intent classification correctness
- Retrieval relevance
- Average response latency
- Escalation precision

## Suggested Demo Targets
- First-contact resolution for scoped issues: >= 70%
- Average response time: <= 5 seconds locally
- Manual intervention reduction: 30% to 40% on repetitive tickets

## Scaling Plan
1. Move document store to Pinecone, Weaviate, or Chroma
2. Add real authentication and RBAC
3. Add audit logging and observability
4. Add feedback loop and human-in-the-loop review
5. Deploy behind an internal gateway with SSO
