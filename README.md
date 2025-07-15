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

## Deployment: Full-Stack Application

This Flask backend is configured to serve both the API and the static files of the React frontend. This means you can deploy the entire application (frontend and backend) to a single server.

### Steps to Deploy (e.g., Heroku, Render, DigitalOcean)

1.  **Build the Frontend:**
    Before deploying the backend, ensure you have built the frontend application. Navigate to your frontend project directory (`mike-care-builds`) and run:
    ```bash
    pnpm run build
    ```
    This will create a `dist` folder. Copy the contents of this `dist` folder into the `src/static` directory of your backend project (`mike-care-builds-backend/src/static`).

2.  **Prepare Backend for Production:**
    -   Ensure you have a `requirements.txt` file with all dependencies (including `gunicorn`).
    -   Use a production-ready WSGI server like Gunicorn instead of the Flask development server. Add `gunicorn` to your `requirements.txt`.

3.  **Create a `Procfile`:**
    Create a file named `Procfile` in the root of your backend repository (`mike-care-builds-backend`) with the following content:
    ```
    web: gunicorn src.main:app
    ```

4.  **Deploy to a Hosting Provider:**
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



