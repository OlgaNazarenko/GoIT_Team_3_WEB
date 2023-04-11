CREATE_COMMENT = """
**Create a new comment in the database:**

- The function takes a field containing the body of the comment and the id of the associated image. 
- If the specified image is not found, the function will return a 404 error. 
- The function returns an object representing the newly created comment.
"""

GET_COMMENTS_BY_IMAGE_OR_USER_ID = """
**Get comments filtered by either image_id or user_id or by user_id and image_id:**

- To retrieve comments by user ID, provide the user_id parameter. 
- Both image_id and user_id parameters can be provided, but at least one must be specified. 
- The skip parameter allows you to skip the first n comments, and the limit parameter limits the number of comments returned. 
- The function returns a list of comment objects. If no comments are found, an empty list will be returned. 
- If both image_id and user_id are not provided, the function will return a 400 error.
"""

GET_COMMENT = """
**Retrieve a comment by its id.**
"""

UPDATE_COMMENT = """
**Updates a comment in the database. Only moderators are allowed to perform this action:**

- The function takes an id of the comment to be updated and contains the new values for each field. 
- The request body should include the comment_id field and one or more optional fields to update such as data. 
- If the specified comment is not found, the function will return a 404 error. 
- If the user is not authorized to perform 
the action, a 403 error will be returned.

"""

REMOVE_COMMENT = """
**Removes a comment from the database. Only moderators are allowed to perform this action:**

- The function takes in an integer representing the id of the comment to be removed and returns a dictionary containing information about that comment. 
- If the specified comment is not found, the function will return a 404 error. 
- If the user is not authorized to perform the action, a 403 error will be returned.

"""