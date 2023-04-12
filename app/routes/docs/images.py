UPLOAD_IMAGE = """
**Uploads an image to the server.**
---

Request Parameters:

- `file`: The image file to upload. Must be a valid image format (PNG, JPEG, etc.).
- `description`: A description of the image. Must be between 10 and 1200 characters long.
- `tag`: Optional. A list of up to 5 tags to add to the image. Each tag must be between 3 and 50 characters long.

Response Parameters:

- `image`: An object containing information about the uploaded image, including the ID, description, tags, and image URL.
- `message`: A message indicating that the image was successfully uploaded.

---

Responses:

- `201 CREATED`: The image was successfully uploaded.
- `422 UNPROCESSABLE ENTITY`: The request was invalid, either because the image file was invalid or because too many tags were specified.
- `401 UNAUTHORIZED`: The user is not authorized to perform this action.
- `429 TOO MANY REQUESTS`: The user has exceeded their rate limit for this action.

---

Example Response:

HTTP/1.1 201 Created
```json

{
"image": {
"id": 12345,
"description": "A beautiful sunset over the beach",
"tags": ["sunset", "beach", "ocean"],
"url": "https://example.com/images/12345"
},
"message": "Image successfully uploaded"
}
  
"""

GET_IMAGES = """
**Returns a list of images matching the specified filters.**

---

Request Parameters:

- `skip`: Optional. The number of images to skip. Defaults to 0.
- `limit`: Optional. The maximum number of images to return. Must be between 1 and 100. Defaults to 10.
- `description`: Optional. A description to filter images by. Must be between 3 and 1200 characters long.
- `tag`: Optional. A tag to filter images by. Must be between 3 and 50 characters long.
- `image_id`: Optional. The ID of an image to filter by.
- `user_id`: Optional. The ID of a user to filter images by.

Response Parameters:

- `id`: The ID of the image.
- `description`: A description of the image.
- `tags`: A list of tags associated with the image.
- `image_url`: The URL of the image.

---

Responses:

- `200 OK`: The list of images was successfully returned.
- `401 UNAUTHORIZED`: The user is not authorized to perform this action.
- `429 TOO MANY REQUESTS`: The user has exceeded their rate limit for this action.

---
Example Response:
```json

{
    "id": 1,
    "description": "Beautiful sunset on the beach",
    "tags": ["nature", "beach", "sunset"],
    "image_url": "https://example.com/images/1"
}

"""

GET_IMAGE = """
**Returns information about a single image.**
---

Request Parameters:

- `image_id`: Required. The ID of the image to retrieve.

---

Response Parameters:

- `id`: The ID of the image.
- `description`: A description of the image.
- `tags`: A list of tags associated with the image.
- `image_url`: The URL of the image.

---

Responses:

- `200 OK`: The image was successfully returned.
- `401 UNAUTHORIZED`: The user is not authorized to perform this action.
- `404 NOT FOUND`: The specified image ID does not exist.
- `429 TOO MANY REQUESTS`: The user has exceeded their rate limit for this action.

---

Example Response:
```json

{
    "id": 1234,
    "description": "A beautiful sunset over the ocean",
    "tags": ["sunset", "ocean", "beauty"],
    "image_url": "https://example.com/images/1234.jpg"
}

"""

UPDATE_IMAGE_DATA = """
**Updates the description and/or tags of an image.**
---

Request Parameters:

- `image_id`: Required. The ID of the image to update. Must be an integer greater than or equal to 1.
- `description`: Required. The new description of the image. Must be between 10 and 1200 characters long.
- `tags`: Optional. A list of tags to associate with the image. Must have between 3 and 50 characters per tag, and no more than 5 tags in total.

---

Response Parameters:

- `id`: The ID of the updated image.
- `description`: The new description of the image.
- `tags`: A list of tags associated with the image.
- `image_url`: The URL of the image.

---

Responses:

- `200 OK`: The image was successfully updated.
- `401 UNAUTHORIZED`: The user is not authorized to perform this action.
- `403 FORBIDDEN`: The user does not have permission to update this image.
- `422 UNPROCESSABLE ENTITY`: The image ID was invalid, or the new description/tags were not valid.

---

Example Request:

```json

{
    "image_id": 123,
    "description": "A new description for the image",
    "tags": ["tag1", "tag2"]
}

"""

DELETE_IMAGE = """
**Deletes the specified image.**
---

Request Parameters:

- `image_id`: Required. The ID of the image to delete.

---

Response Parameters:

- `message`: A message indicating whether the deletion was successful.

---

Responses:

- `200 OK`: The image was successfully deleted.
- `401 UNAUTHORIZED`: The user is not authorized to perform this action.
- `403 FORBIDDEN`: The user is not allowed to delete the specified image.
- `404 NOT FOUND`: The specified image could not be found.
- `429 TOO MANY REQUESTS`: The user has exceeded their rate limit for this action.

---

Example Response:

HTTP/1.1 200 OK
- Content-Type: application/json
```json

{
    "message": "Image successfully deleted"
}


"""