from io import BytesIO

import qrcode
from starlette.responses import StreamingResponse


class QRService:

    @classmethod
    async def crate_qr_for_url(cls, image_url, version: int, box_size: int, border: int,
                         fit: bool = True) -> StreamingResponse:
        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(image_url)
        qr.make(fit=fit)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        qr_img.save(buffer)
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="image/png")
