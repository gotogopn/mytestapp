
# Use the official Python image from the Docker Hub
FROM python:3.12.7

# Set the working directory in the container
WORKDIR /myapp

# Copy the requirements file into the container
COPY ./myapp/requirements.txt  ./

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p ./myapp/static/uploads/

RUN chmod -R 777 ./myapp/static/uploads/

# Copy the rest of the application code into the container
COPY .  .

#CMD ["python", "./myapp/app.py"]

# Expose the port that the app runs on
EXPOSE 5001

# Define the command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]
