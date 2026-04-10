FROM n8nio/n8n:latest

USER root

# Copy VNSO branding assets - overwrite default n8n logos
COPY assets/favicon.ico /usr/local/lib/node_modules/n8n/node_modules/n8n-editor-ui/dist/favicon.ico
COPY assets/n8n-logo.png /usr/local/lib/node_modules/n8n/node_modules/n8n-editor-ui/dist/static/n8n-logo.png

# Patch index.html title from "n8n" to "VNSO"
RUN sed -i 's/n8n\.io - Workflow Automation/VNSO - Workflow Automation/g' \
    /usr/local/lib/node_modules/n8n/node_modules/n8n-editor-ui/dist/index.html 2>/dev/null || true

USER node
