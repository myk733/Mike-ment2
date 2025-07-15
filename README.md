
# Mike Care Builds - Backend

This is the backend application for Mike Care Builds, a mobile mental health and wellness app tailored for Kenyan users.

## How to Run the App Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/myk733/Mike-ment2.git
    cd Mike-ment2
    ```
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Start the development server:**
    ```bash
    python src/main.py
    ```
    The backend will be running at `http://localhost:5000`.

## Deployment

### Full-Stack Deployment (e.g., Heroku, Render, DigitalOcean)

Since this is a full-stack application with a Flask backend, you need a hosting provider that supports Python applications. Here are general steps for deployment:

1.  **Prepare for Production:**
    -   Ensure you have a `requirements.txt` file with all dependencies.
    -   Use a production-ready WSGI server like Gunicorn instead of the Flask development server. You can add `gunicorn` to your `requirements.txt`.

2.  **Create a `Procfile`:**
    Create a file named `Procfile` in the root of your backend repository with the following content:
    ```
    web: gunicorn src.main:app
    ```

3.  **Deploy to a Hosting Provider:**
    -   **Heroku:**
        -   Create a new Heroku app.
        -   Connect your GitHub repository to the Heroku app.
        -   Enable automatic deployments from the `master` branch.
        -   Heroku will automatically detect the `Procfile` and `requirements.txt` and deploy your application.

    -   **Render:**
        -   Create a new Web Service on Render.
        -   Connect your GitHub repository.
        -   Set the build command to `pip install -r requirements.txt`.
        -   Set the start command to `gunicorn src.main:app`.

    -   **DigitalOcean App Platform:**
        -   Create a new App on DigitalOcean.
        -   Connect your GitHub repository.
        -   DigitalOcean will automatically detect the Python application and suggest build and run commands.

### Important Notes

-   **Database:** For production, you should use a more robust database like PostgreSQL or MySQL instead of SQLite. Most hosting providers offer managed database services.
-   **Environment Variables:** Store sensitive information like secret keys and database URLs in environment variables, not in your code.
-   **Static Files:** For better performance, you can serve your static files (the React frontend) from a separate CDN or static hosting service.



