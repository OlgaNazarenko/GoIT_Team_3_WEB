CREATE_COMMENT = """
**Creates a new comment on an image.**
---

Request Parameters:

- `image_id`: Required. The ID of the image to add the comment to.
- `data`: Required. The text of the comment. Must be between 1 and 500 characters long.

---

Response Parameters:

- `id`: The ID of the comment.
- `user_id`: The ID of the user who created the comment.
- `image_id`: The ID of the image the comment is on.
- `data`: The text of the comment.
- `created_at`: The timestamp when the comment was created.

---

Responses:

- `201 CREATED`: The comment was successfully created.
- `401 UNAUTHORIZED`: The user is not authorized to perform this action.
- `404 NOT FOUND`: The specified image was not found.

---

Example Request:
- POST /api/v1/comments HTTP/1.1
- Host: example.com
- Content-Type: application/json
- Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...


    {
        "image_id": 123,
        "data": "This is a great photo!"
    }


---

Example Response:

HTTP/1.1 201 Created
- Content-Type: application/json
```json

{
    "id": 456,
    "user_id": 789,
    "image_id": 123,
    "data": "This is a great photo!",
    "created_at": "2023-03-22T10:00:00Z"
}

"""

GET_COMMENTS_BY_IMAGE_OR_USER_ID = """
**Retrieves comments by image ID or user ID.**

---

Query Parameters:

- `image_id`: Optional. The ID of the image to retrieve comments for.
- `user_id`: Optional. The ID of the user to retrieve comments for.
- `skip`: Optional. The number of comments to skip. Defaults to 0.
- `limit`: Optional. The maximum number of comments to retrieve. Defaults to 10.

---

Response Parameters:

- `id`: The ID of the comment.
- `user_id`: The ID of the user who created the comment.
- `image_id`: The ID of the image the comment is on.
- `data`: The text of the comment.
- `created_at`: The timestamp when the comment was created.

---

Responses:

- `200 OK`: The comments were successfully retrieved.
- `400 BAD REQUEST`: Both image_id and user_id were not provided.
- `401 UNAUTHORIZED`: The user is not authorized to perform this action.
- `404 NOT FOUND`: The specified image or user was not found.

---

Example Request:
- GET /api/v1/comments?image_id=123 HTTP/1.1
- Host: example.com
- Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

---

Example Response:

HTTP/1.1 200 OK
- Content-Type: application/json
```json

{
    "id": 456,
    "user_id": 789,
    "image_id": 123,
    "data": "This is a great photo!",
    "created_at": "2023-03-22T10:00:00Z"
},
{
    "id": 789,
    "user_id": 123,
    "image_id": 123,
    "data": "I agree, it's beautiful!",
    "created_at": "2023-03-22T10:01:00Z"
}

"""
GET_COMMENT = """
**Get a single comment by ID.**
---

Request Parameters:

- `comment_id`: Required. The ID of the comment to retrieve.

---

Response Parameters:

- `id`: The ID of the comment.
- `user_id`: The ID of the user who created the comment.
- `image_id`: The ID of the image the comment is on.
- `data`: The text of the comment.
- `created_at`: The timestamp when the comment was created.

---

Responses:

- `200 OK`: The comment was successfully retrieved.
- `401 UNAUTHORIZED`: The user is not authorized to perform this action.
- `404 NOT FOUND`: The specified comment was not found.

---

Example Request:
- GET /api/v1/comments/123 HTTP/1.1
- Host: example.com
- Content-Type: application/json
- Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

---

Example Response:

HTTP/1.1 200 OK
- Content-Type: application/json
```json

{
    "id": 123,
    "user_id": 456,
    "image_id": 789,
    "data": "This is a great photo!",
    "created_at": "2023-03-22T10:00:00Z"
}

"""

UPDATE_COMMENT = """
**This API endpoint updates an existing comment in the system. It can be accessed by users with moderator role.**
---

Request Parameters:

- `comment_id`: Required. The ID of the comment to update.
- `data`: Required. The new text for the comment. Must be between 1 and 500 characters long.

---

Response Parameters:

- `id`: The ID of the comment.
- `user_id`: The ID of the user who created the comment.
- `image_id`: The ID of the image the comment is on.
- `data`: The text of the comment.
- `created_at`: The timestamp when the comment was created.

---

Responses:

- `200 OK`: The comment was successfully updated.
- `401 UNAUTHORIZED`: The user is not authorized to perform this action.
- `404 NOT FOUND`: The specified comment was not found.

---

Example Request:
- PUT /api/v1/comments HTTP/1.1
- Host: example.com
- Content-Type: application/json
- Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...


{
    "comment_id": 456,
    "data": "This is a new comment"
}


---

Example Response:

- HTTP/1.1 200 OK
- Content-Type: application/json

```json

{
    "id": 456,
    "user_id": 789,
    "image_id": 123,
    "data": "This is a new comment",
    "created_at": "2023-03-22T10:00:00Z"
}

"""

REMOVE_COMMENT = """
**Deletes the comment with the specified ID.**
---

Request Parameters:

- `comment_id`: Required. The ID of the comment to delete.

---

Responses:

- `200 OK`: The comment was successfully deleted.
- `401 UNAUTHORIZED`: The user is not authorized to perform this action.
- `404 NOT FOUND`: The specified comment was not found.

---

Example Request:
- DELETE /api/v1/comments/123 HTTP/1.1
- Host: example.com
- Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

---

Example Response:

- HTTP/1.1 200 OK
- Content-Type: application/json

```json

{
    "id": 123,
    "user_id": 456,
    "image_id": 789,
    "data": "This is a great photo!",
    "created_at": "2023-03-22T10:00:00Z"
}
"""