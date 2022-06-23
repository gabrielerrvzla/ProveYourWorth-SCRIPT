import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
from shutil import copyfile
from pathlib import Path


class JobTest:
    _base_url = "https://www.proveyourworth.net/level3"
    _session_id = None
    _token = None
    _response = requests.Session()
    _file_path = Path("./")

    def __init__(self, name: str, email: str, cv: str):
        """ 
        Constructor
        """
        self.name = name
        self.email = email
        self.cv = cv

    def _print_step(self, message: str) -> None:
        """ 
        Print step
        """
        print("*" * 50)
        print(message)
        return

    def _get_session_id(self) -> None:
        """
        Get session id from _response header and save it to variable
        """
        request = self._response.get(self._base_url)
        session_id = request.cookies['PHPSESSID']
        self._session_id = session_id
        self._print_step(f"Get session id: {session_id}")

    def _get_token(self) -> None:
        """
        Get token from _response header and save it to variable
        """
        request = self._response.get(self._base_url)
        soup = BeautifulSoup(request.text, 'html.parser')
        self._token = soup.find('input', {'name': 'statefulhash'})['value']
        self._print_step(f"Get token: {self._token}")

    def _activate_account(self):
        """
        Activate account with token
        """
        request = self._response.get(
            f'{self._base_url}/activate?statefulhash={self._token}'
        )

        self._print_step(request.text)

    def _get_image(self) -> bytes:
        """
        Get image from _response and save it to file 
        """
        request = self._response.get(
            f"{self._base_url}/payload",
            stream=True
        )
        image = request.raw
        return image

    def _sing_image(self) -> None:
        """
        Sing image with name 
        """

        image = Image.open(self._get_image())
        draw = ImageDraw.Draw(image)
        draw.text(
            (image.width / 2, image.height / 2),
            f"{self.name}, Hash: {self._token}",
            fill=(255, 255, 255),
        )
        image.save("image.jpg", "JPEG")
        self._print_step("Sing image successfully")

    def _code_copy(self) -> None:
        """ 
        Copy code to file
        """
        copyfile("main.py", "code.py")
        self._print_step("Copy code successfully")

    def _form_submit(self) -> None:
        """
        Submit form with image and cv
        """
        payload = self._response.get(f"{self._base_url}/payload")
        url = payload.headers['X-Post-Back-To']

        files = {
            "code": open(self._file_path / "code.py", "rb"),
            "resume": open(self._file_path / "resume.pdf", "rb"),
            "image": open(self._file_path / "image.jpg", "rb")
        }

        data = {
            "email": self.email,
            "name": self.name,
            "aboutme": "I'm backend developer from Venezuela, I'm a Python developer.",
        }

        request = self._response.post(
            url,
            files=files,
            data=data,
        )

        self._print_step(request.status_code)
        self._print_step(request.text)

    def main(self) -> None:
        """
        Main function
        """
        self._get_session_id()
        self._get_token()
        self._activate_account()
        self._sing_image()
        self._code_copy()
        self._form_submit()


if __name__ == "__main__":
    name = input("Name: ")
    email = input("Email: ")
    job_test = JobTest(name, email, "cv.pdf")
    job_test.main()
