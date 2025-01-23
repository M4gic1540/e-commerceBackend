# E-commerce API

This is an e-commerce API built with Django, Django REST framework, and JWT for authentication.

## Features

- User registration and authentication
- Product listing and details
- Shopping cart management
- Order processing
- JWT-based authentication

## Technologies Used

- Django
- Django REST framework
- JWT (JSON Web Tokens)

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Apply migrations:
    ```bash
    python manage.py migrate
    ```

5. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```bash
    python manage.py runserver
    ```

## API Endpoints

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login and obtain JWT token
- `GET /api/products/` - List all products
- `GET /api/products/<id>/` - Retrieve product details
- `POST /api/cart/` - Add item to cart
- `GET /api/cart/` - View cart items
- `POST /api/orders/` - Create a new order

## Authentication

This API uses JWT for authentication. To access protected endpoints, include the JWT token in the `Authorization` header:

```
Authorization: Bearer <your-token>
```

## License

This project is licensed under the MIT License.

## Contact

For any inquiries, please contact [your-email@example.com].
