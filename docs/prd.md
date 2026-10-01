This workflow reviews a repository's Docker setup:

1. Run the documented build command.
2. Report the outcome.
3. Recommend whether the repository is ready to proceed.

Trigger: Developer invokes claude "review Docker setup" to start the Docker setup review workflow.

Decision Events:

1. Build Succeeds: The Docker build completes successfully. Agent recommends proceeding with the repository.
2. Build Fails: The Docker build fails. Agent recommends not proceeding with the repository. Agent does not attempt to fix the build.

Actions list:

1. Read documentation to identify the documented build command.
2. Run Docker build command inside the sandbox environment.
3. Record the outcome of the Docker build.
4. Evaluate the build outcome.
5. Summarize errors and warnings in the build output.
6. Provide a recommendation based on the evaluation of the build outcome.

Acceptance criteria:

1. The agent correctly identifies whether the Docker image was built successfully or failed.
2. The summary includes all warnings and errors present in the build output; it does not omit any.
3. The recommendation is consistent with the build result.
4. The agent did not push, publish, or deploy anything.
