# Chatbot Appointment Website

This project is a Django-based web application designed to facilitate user interactions with a chatbot before a doctor's appointment. The chatbot utilizes a pre-trained language model from the [Meditron GitHub repository](https://github.com/epfLLM/meditron) to provide users with relevant information and assistance.

## Project Structure

The project is organized into several key components:

- **chatbot_website**: The main Django project directory containing settings, URL routing, and WSGI/ASGI entry points.
- **chatbot**: The application responsible for handling user interactions with the chatbot, including views, models, and templates.
- **reports**: The application that generates and displays reports based on user interactions with the chatbot.
- **meditron**: The directory containing the implementation of the Meditron language model, including utilities for processing user input.

## Requirements

To run this project, you need to have the following installed:

- Python 3.x
- Django
- MySQL

You can install the required Python packages using the following command:

```
pip install -r requirements.txt
```

## Database Configuration

This project uses MySQL as the database. Make sure to configure your MySQL database settings in `chatbot_website/settings.py` before running the application.

## Running the Application

To start the development server, navigate to the project directory and run:

```
python manage.py runserver
```

You can then access the application at `http://127.0.0.1:8000/`.

## Usage

1. Visit the main landing page to interact with the chatbot.
2. The chatbot will guide you through the appointment process and answer any questions you may have.
3. After the interaction, you can view generated reports in the reports section.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.