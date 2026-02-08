# Data Model: Deploy Todo Chatbot on Minikube with Docker and Helm

## Kubernetes Resources

### Deployment
- **Name**: Unique identifier for the deployment
- **Replicas**: Number of pod instances to maintain
- **Selector**: Labels to identify pods controlled by this deployment
- **Template**: Pod template specifying container configuration
- **Strategy**: Update strategy (RollingUpdate, Recreate)

### Service
- **Name**: Unique identifier for the service
- **Type**: Service type (ClusterIP, NodePort, LoadBalancer, ExternalName)
- **Ports**: Port mappings (port, targetPort, protocol)
- **Selector**: Labels to identify pods to route traffic to

### ConfigMap
- **Name**: Unique identifier for the ConfigMap
- **Data**: Key-value pairs of configuration data
- **BinaryData**: Binary data (if needed)

### Secret
- **Name**: Unique identifier for the secret
- **Data**: Base64 encoded secret data
- **StringData**: Unencoded secret data (encoded automatically)

### Ingress
- **Name**: Unique identifier for the ingress
- **Rules**: Host and path mappings to services
- **TLS**: TLS certificate configuration
- **Annotations**: Ingress controller specific configurations

### PersistentVolumeClaim (if needed)
- **Name**: Unique identifier for the PVC
- **AccessModes**: How the volume should be mounted
- **Resources**: Storage request and limits
- **StorageClassName**: Storage class to use

## Helm Chart Structure

### Chart.yaml
- **Name**: Chart name
- **Version**: Chart version (semantic versioning)
- **Description**: Brief description of the chart
- **Dependencies**: List of chart dependencies

### values.yaml
- **image**: Container image configuration (repository, tag, pullPolicy)
- **replicaCount**: Number of pod replicas
- **resources**: Resource limits and requests
- **service**: Service configuration (type, ports)
- **ingress**: Ingress configuration
- **env**: Environment variables
- **config**: Configuration parameters

### Templates
- **deployment.yaml**: Deployment resource template
- **service.yaml**: Service resource template
- **ingress.yaml**: Ingress resource template
- **configmap.yaml**: ConfigMap resource template
- **secret.yaml**: Secret resource template
- **_helpers.tpl**: Named templates for reuse

## Docker Build Configuration

### Multi-stage Build Stages
- **Build Stage**: Contains build tools and dependencies
- **Runtime Stage**: Minimal runtime environment
- **Artifacts**: Files transferred between stages

### Build Arguments
- **NODE_ENV**: Node.js environment (development, production)
- **PYTHON_VERSION**: Python version for runtime
- **BUILD_DEPS**: Dependencies needed only for build
- **RUNTIME_DEPS**: Dependencies needed for runtime

## Health Check Configuration

### Liveness Probe
- **Path**: HTTP endpoint to check (for HTTP probes)
- **Command**: Command to execute (for exec probes)
- **InitialDelaySeconds**: Delay before first probe
- **PeriodSeconds**: Interval between probes
- **TimeoutSeconds**: Timeout for each probe
- **FailureThreshold**: Number of failures before restart

### Readiness Probe
- **Path**: HTTP endpoint to check (for HTTP probes)
- **Command**: Command to execute (for exec probes)
- **InitialDelaySeconds**: Delay before first probe
- **PeriodSeconds**: Interval between probes
- **TimeoutSeconds**: Timeout for each probe
- **FailureThreshold**: Number of failures before removing from service