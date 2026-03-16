# mycodex-skills

Portable backup of my Codex user skills.

## Included layout

All skills are stored under `skills/`.

To import them on another machine:

```bash
mkdir -p ~/.codex/skills
cp -a skills/* ~/.codex/skills/
```

Then restart Codex so the new skills are picked up.

## Included Skills

- `api-gateway`: AWS API Gateway for REST and HTTP API management. Use when creating APIs, configuring integrations, setting up authorization, managing stages, implementing rate limiting, or troubleshooting API issues.
- `bedrock`: AWS Bedrock foundation models for generative AI. Use when invoking foundation models, building AI applications, creating embeddings, configuring model access, or implementing RAG patterns.
- `bucketmanager-s3control-e2e`: Local bucketmanager S3Control end-to-end testing workflow. Use when rebuilding `bkt-mgr`, preparing bitmap-based test data, running multi-s3gw parent/child job validation, or measuring memory peaks in this local environment.
- `claude-mem-codex`: Use claude-mem from Codex via a Codex-specific wrapper, MCP registration, and `~/.codex`-backed data paths.
- `cloudformation`: AWS CloudFormation infrastructure as code for stack management. Use when writing templates, deploying stacks, managing drift, troubleshooting deployments, or organizing infrastructure with nested stacks.
- `cloudwatch`: AWS CloudWatch monitoring for logs, metrics, alarms, and dashboards. Use when setting up monitoring, creating alarms, querying logs with Insights, configuring metric filters, building dashboards, or troubleshooting application issues.
- `cognito`: AWS Cognito user authentication and authorization service. Use when setting up user pools, configuring identity pools, implementing OAuth flows, managing user attributes, or integrating with social identity providers.
- `dynamodb`: AWS DynamoDB NoSQL database for scalable data storage. Use when designing table schemas, writing queries, configuring indexes, managing capacity, implementing single-table design, or troubleshooting performance issues.
- `ec2`: AWS EC2 virtual machine management for instances, AMIs, and networking. Use when launching instances, configuring security groups, managing key pairs, troubleshooting connectivity, or automating instance lifecycle.
- `ecs`: AWS ECS container orchestration for running Docker containers. Use when deploying containerized applications, configuring task definitions, setting up services, managing clusters, or troubleshooting container issues.
- `eks`: AWS EKS Kubernetes management for clusters, node groups, and workloads. Use when creating clusters, configuring IRSA, managing node groups, deploying applications, or integrating with AWS services.
- `eventbridge`: AWS EventBridge serverless event bus for event-driven architectures. Use when creating rules, configuring event patterns, setting up scheduled events, integrating with SaaS, or building cross-account event routing.
- `fuse`: Build, debug, and review Linux FUSE filesystems with the official libfuse userspace library. Use when implementing a FUSE filesystem, choosing between libfuse high-level vs low-level APIs, wiring callbacks, building with fuse3/pkg-config, mounting for local testing, or troubleshooting fusermount3 and permission issues.
- `iam`: AWS Identity and Access Management for users, roles, policies, and permissions. Use when creating IAM policies, configuring cross-account access, setting up service roles, troubleshooting permission errors, or managing access control.
- `lambda`: AWS Lambda serverless functions for event-driven compute. Use when creating functions, configuring triggers, debugging invocations, optimizing cold starts, setting up event source mappings, or managing layers.
- `openai-docs`: Use when the user asks how to build with OpenAI products or APIs and needs up-to-date official documentation with citations, especially for Codex, Responses API, Chat Completions, Apps SDK, Agents SDK, Realtime, and model capabilities or limits.
- `rds`: AWS RDS relational database service for managed databases. Use when provisioning databases, configuring backups, managing replicas, troubleshooting connectivity, or optimizing performance.
- `s3`: AWS S3 object storage for bucket management, object operations, and access control. Use when creating buckets, uploading files, configuring lifecycle policies, setting up static websites, managing permissions, or implementing cross-region replication.
- `secrets-manager`: AWS Secrets Manager for secure secret storage and rotation. Use when storing credentials, configuring automatic rotation, managing secret versions, retrieving secrets in applications, or integrating with RDS.
- `sns`: AWS SNS notification service for pub/sub messaging. Use when creating topics, managing subscriptions, configuring message filtering, sending notifications, or setting up mobile push.
- `sqs`: AWS SQS message queue service for decoupled architectures. Use when creating queues, configuring dead-letter queues, managing visibility timeouts, implementing FIFO ordering, or integrating with Lambda.
- `step-functions`: AWS Step Functions workflow orchestration with state machines. Use when designing workflows, implementing error handling, configuring parallel execution, integrating with AWS services, or debugging executions.
- `stream-coding`: Documentation-first development methodology focused on producing AI-ready specs before implementation. Use when you want to clarify requirements, produce executable specs, and reduce code-generation ambiguity.
- `tgtool`: Routes tasks through the best local Codex skills, chooses execution mode, consults tool-advisor first, and now proactively considers persistent memory (`claude-mem`) and live web research (`exa`) when useful.
- `tool-advisor`: Discovers the available tool environment and suggests suitable tool combinations for a task without executing actions.

## Notes

- These are user-installed skills only.
- System skills under `~/.codex/skills/.system` are not mirrored here.
