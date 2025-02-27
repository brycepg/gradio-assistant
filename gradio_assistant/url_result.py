from dataclasses import dataclass

@dataclass
class UrlResult:
    content: str
    url: str

    def to_dict(self):
        return {
            "content": self.content,
            "url": self.url,
        }
