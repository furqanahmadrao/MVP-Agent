
This guide explains how to build, serve, and deploy the project documentation.

## Serving Locally

To preview the documentation site on your local machine, run the following command from the root of the project repository:

` + "```" + `bash
mkdocs serve
` + "```" + `

This will start a local development server, and you can view the documentation by opening your web browser to `http://127.0.0.1:8000/`. The site will automatically reload whenever you make changes to the documentation files.

## Deploying to GitHub Pages

The documentation is designed to be deployed to GitHub Pages. To deploy the site, use the following command:

` + "```" + `bash
mkdocs gh-deploy
` + "```" + `

This command will build the documentation, commit it to the `gh-pages` branch, and push it to GitHub. The site will then be available at `https://<your-username>.github.io/<repository-name>/`.

**Note:** You must have the necessary permissions to push to the repository for this command to work.
