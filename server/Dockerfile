FROM python:3.8

WORKDIR /server

# Copy the entire project to the container
COPY . /server/

COPY ./requirements.txt /server/
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Command to run your app
CMD ["python", "app.py"]
