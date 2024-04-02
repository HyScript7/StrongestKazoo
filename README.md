<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/HyScript7/StrongestKazoo">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">The Strongest Kazoo</h3>

  <p align="center">
    A discord music bot with youtube support written in python
    <br />
    <a href="#"><strong>Explore the docs »</strong></a> <!-- TODO: Link to docs -->
    <br />
    <br />
    <a href="#getting-started">Get Started</a>
    ·
    <a href="https://github.com/HyScript7/StrongestKazoo/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/HyScript7/StrongestKazoo/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Strongest Kazoo is a discord bot with support for youtube videos, written in python 3.11 using discord.py 2.3.2

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python.org]][Python-url]
* [![Poetry][Poetry.org]][Poetry-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

* [poetry](https://python-poetry.org/docs)
* [python](http://python.org/)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/HyScript7/StrongestKazoo.git
   ```
2. Install environment
   ```sh
   poetry install
   ```
3. Copy example.env as .env and set your token value
4. Run the app module
   ```sh
   poetry run python3 -m app
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

To use the bot, add your discord bot application to your server. Then re-run the bot to force commands to sync.

Afterwards, type `/` to view a list of avabiable commands.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Youtube Support
  - [x] Playlist Support
  - [x] Metadata Cache
  - [x] Fragmenting
    - [ ] Seemless fragmenting
    - [x] Fragment Cache
- [ ] Spotify Support
  - ...
- [ ] Soundcloud Support
  - ...
- [ ] Playlists (Store and load your queue)
- [ ] Web UI

See the [open issues](https://github.com/HyScript7/StrongestKazoo/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.md` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@hyscript7](https://twitter.com/hyscript7) - hyscript7@gmail.com

Project Link: [https://github.com/HyScript7/StrongestKazoo](https://github.com/HyScript7/StrongestKazoo)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [yt_dlp](https://github.com/yt-dlp/yt-dlp)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/HyScript7/StrongestKazoo.svg?style=for-the-badge
[contributors-url]: https://github.com/HyScript7/StrongestKazoo/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/HyScript7/StrongestKazoo.svg?style=for-the-badge
[forks-url]: https://github.com/HyScript7/StrongestKazoo/network/members
[stars-shield]: https://img.shields.io/github/stars/HyScript7/StrongestKazoo.svg?style=for-the-badge
[stars-url]: https://github.com/HyScript7/StrongestKazoo/stargazers
[issues-shield]: https://img.shields.io/github/issues/HyScript7/StrongestKazoo.svg?style=for-the-badge
[issues-url]: https://github.com/HyScript7/StrongestKazoo/issues
[license-shield]: https://img.shields.io/github/license/HyScript7/StrongestKazoo.svg?style=for-the-badge
[license-url]: https://github.com/HyScript7/StrongestKazoo/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
[Python.org]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: http://python.org/
[Poetry.org]: https://img.shields.io/badge/Poetry-%233B82F6.svg?style=for-the-badge&logo=poetry&logoColor=0B3D8D
[Poetry-url]: https://python-poetry.org/
