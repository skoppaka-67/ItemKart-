# ItemKart
Online E-commerce store 


#security 

Implemented token based authentication and authorization using JWT and HTTPBasicAuth .


# home page

Home page will contains list of item tags.

url for homepage : http://localhost:5000/home

Required no credentials 

# Category api

Based on selection in home page, Items belonging to the selected tag will be returned with the pagination and back and forth navigation urls. 


Required no credentials 

# Add to cart 

Automatically redirects to login page for authentication or on JWT token  expiration.

Once after successful login user can add item to cart with item name.

url for add to cart : http://localhost:5000/add_to_cart

# Show cart

Displays items in the cart.

Url : http://localhost:5000/show_cart

# Delete item from the cart.

Api will Allows only authorized users to delete from the cart.

url : http://localhost:5000/remove_cart

# logout 

Logout the user by destroying session and redirects to login page.

url : http://localhost:5000/logout
