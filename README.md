This repository contains the code, templates, and sample required to automatically create a Virtual Customer Service Representative as described on the Pandorabots Blog [here](http://blog.pandorabots.com/creating-a-virtual-customer-service-representative/). If you are curious about what this code does, be sure to read the post, as well as any others that might pique your interest. The following is a short usage guide:

Download the Virtual_Guide_Generator.py program and one of our Question and Answer Templates. There is a sample Q&A document of each acceptable file type that shows proper formatting.

The program is written in python, and it makes use of the [Pandorabots Python SDK](https://github.com/pandorabots/pb-python), so it is essential you have both python and that package installed. Use pip to install the Pandorabots Python SDK:

    username% pip install PbPython

To make your bot:

    username% python Virtual_Guide_Generator.py --input-file 'Q&A_template.txt'

To update your bot with a revised Q&A Template:

    username% python Virtual_Guide_Generator.py --input-file 'Q&A_template.txt' --update True

Happy Botmaking!
