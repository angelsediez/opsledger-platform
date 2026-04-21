# CI/CD Pipeline

## Planned Stages

1. Checkout source
2. Create/activate Python environment
3. Install dependencies
4. Run tests
5. Build application image
6. Deploy inactive color
7. Run health validation
8. Switch Nginx upstream
9. Keep previous color available for rollback

## Jenkins Model

- Jenkinsfile in repository
- controller coordinates
- agent executes build/test/deploy tasks

