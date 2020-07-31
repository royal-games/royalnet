import json
from typing import *
from royalnet.constellation import PageStar
from royalnet.constellation.api import ApiStar
from starlette.requests import Request
from starlette.responses import Response, HTMLResponse
import royalnet


backtick = "\u0060"


class DocsStar(PageStar):
    path = "/docs"

    async def page(self, request: Request) -> Response:
        paths = {}

        for star in self.constellation.stars:
            if not isinstance(star, ApiStar):
                continue
            paths[star.path] = star.swagger()

        spec = json.dumps({
            "openapi": "3.0.0",
            "info": {
                "description": "Autogenerated Royalnet API documentation",
                "title": "Royalnet",
                "version": f"{royalnet.__version__}",
            },
            "paths": paths,
            "components": {
                "securitySchemes": {
                    "RoyalnetLoginToken": {
                        "type": "apiKey",
                        "in": "query",
                        "name": "token",
                    }
                }
            }
        })

        return HTMLResponse(
            f"""
            <html lang="en">
                <head>
                    <title>Royalnet Docs</title>
                    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.23.4/swagger-ui.css">
                    <script src="https://unpkg.com/swagger-ui-dist@3.23.4/swagger-ui-bundle.js"></script>
                    <script src="https://unpkg.com/swagger-ui-dist@3.23.4/swagger-ui-standalone-preset.js"></script>
                </head>
                <body>
                    <div style="display: none;">{spec}</div>
                    <div id="docs"/>
                    <script>
                        const ui = SwaggerUIBundle({{
                            spec: JSON.parse(String.raw`{spec}`),
                            dom_id: '#docs',
                            presets: [
                                SwaggerUIBundle.presets.apis,
                                SwaggerUIStandalonePreset
                            ],
                            layout: "StandaloneLayout"
                        }})
                    </script>
                </body>
            </html>
            """
        )
