import re
from markupsafe import Markup

def embed_media(content):
    print("embed_media called with:", content)
    # YouTube (youtube.com and youtu.be)
    yt_pattern = re.compile(r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([-\w]+))')
    # Vimeo
    vimeo_pattern = re.compile(r'(https?://vimeo\.com/(\d+))')
    # Images
    img_pattern = re.compile(r'(https?://\S+\.(?:png|jpg|jpeg|gif))')

    content = yt_pattern.sub(
        r'<iframe width="400" height="225" src="https://www.youtube.com/embed/\2" frameborder="0" allowfullscreen></iframe>',
        content
    )
    content = vimeo_pattern.sub(
        r'<iframe src="https://player.vimeo.com/video/\2" width="400" height="225" frameborder="0" allowfullscreen></iframe>',
        content
    )
    content = img_pattern.sub(
        r'<img src="\1" alt="image" style="max-width:400px;">',
        content
    )
    print("embed_media returning:", content)
    return Markup(content)