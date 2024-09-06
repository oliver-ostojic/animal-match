from django.db import models, transaction
from django.core.exceptions import ValidationError

from matcher.utils import fetch_animal_data_from_api, fetch_image_url_from_api
import random


class User(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    @staticmethod
    def take_quiz(quiz_id, responses):
        # Start a transaction block
        try:
            with transaction.atomic():
                # Fetch the quiz based on the provided quiz_id
                quiz = Quiz.objects.get(id=quiz_id)
                # Validate responses
                if not quiz.validate_response(responses):
                    raise ValidationError("Invalid response")
                # Create QuizResult object
                result = QuizResult.objects.create(responses=responses, quiz=quiz)
                # Calculate score and find match!
                result.calculate_score()
                # Increase the value for times_taken in quiz
                quiz.times_taken += 1
                quiz.save()
                # Return the result object created
                return result
        # If quiz is not fetched (e.g. does not exist)
        except Quiz.DoesNotExist:
            # If quiz_id does not exist, raise error
            raise ValueError("Quiz not found")
        # Handle validation error
        except ValidationError as e:
            raise e


class Quiz(models.Model):
    # A valid name is an animal name such as 'frog'
    title = models.CharField(max_length=50, unique=True)
    times_taken = models.IntegerField(default=0)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

    @classmethod
    def retrieve_quiz_by_popularity_rank(cls, rank):
        """
        This class method returns the quiz of (rank) popularity that is inputted.
        """
        # Order quizzes using Django method
        quizzes = Quiz.objects.all().order_by('-times_taken')
        return quizzes[rank - 1]

    @staticmethod
    def validate_response(responses):
        """
        Validates the user's responses. This method checks if exactly 5 responses have been
        provided and ensures that all are valid (e.g. non-empty strings). If validation
        fails, raises ValidationError.

        :param responses: A list of user responses to validate
        :return: True if responses are valid, otherwise raises error
        """
        # Check to see if responses are in a list
        if not isinstance(responses, dict):
            raise ValidationError("responses must be a dict")

        # Check to see if 5 responses are given
        if not len(responses) == 4:
            raise ValidationError("responses must have exactly 3 items")

        # Check to see that each response is a non-empty string
        for response in responses:
            if not isinstance(response, str) or not response.strip():
                raise ValidationError("Invalid response: {response} must be a string")

        return True

    @classmethod
    def validate_and_create_quiz(cls, animal_search):
        """
        Validate whether an animal search can generate a quiz or not. If passed,
        create the quiz and if not, raise ValidationError. Complete quiz generation includes
        creating its questions and answers.
        :return: quiz object that is created
        """
        # If the API generates an animal, proceed to validate animal
        try:
            # Call the API on the animal
            animal_data = fetch_animal_data_from_api(animal_search)
            # Raise error if animal_data is empty
            if len(animal_data) == 0:
                raise ValueError("Animal search yielded no results: unable to generate quiz.")
            # Try validating animal
            valid_animals, answers = Quiz.validate_quiz(animal_data)
            # Start an atomic transaction
            with transaction.atomic():
                # Create quiz
                quiz = Quiz.objects.create(title=animal_search.title())
                # Set the quiz image URL
                image_url = fetch_image_url_from_api(animal_search)
                quiz.image_url = image_url
                quiz.save()
                # Create the quiz's animals
                for animal in valid_animals:
                    # Get image_url (returns, url or None)
                    url = fetch_image_url_from_api(animal['name'])
                    # Create the animal
                    Animal.objects.create(name=animal['name'],
                                          species=animal['taxonomy']['scientific_name'],
                                          habitat=animal['characteristics']['habitat'],
                                          lifestyle=animal['characteristics'].get('lifestyle', None),
                                          locations=animal['locations'],
                                          diet=animal['characteristics']['diet'],
                                          group_behavior=animal['characteristics'].get('group_behavior', None),
                                          lifespan=animal['characteristics']['lifespan'],
                                          image_url=url,
                                          quiz=quiz
                                          )
                # Now create the quiz's questions and its answers
                for key, value in answers.items():
                    # First make sure that 'value', or the unique answers, is not empty
                    if len(value) > 0:
                        question = Question.objects.create(
                            category=key,
                            quiz=quiz
                        )
                        for answer in value:
                            Answer.objects.create(
                                question=question,
                                text=answer,
                            )
                return quiz
        # Else, raise Validation Error
        except ValidationError as e:
            raise e

    @classmethod
    def validate_quiz(cls, animal_data):
        """
        This function takes animal_data (taken from API call) and validates whether enough valid animals
        exist to create a quiz, and whether enough unique animal attributes exist to make a quiz
        :return: list of valid animals that can create a quiz, otherwise return an error
        """
        valid_animals = []
        # Validate that an animal has all required fields
        for animal_dict in animal_data:
            validated = Animal.validate_animal_data(animal_data=animal_dict)
            try:
                animal = Animal.objects.get(name=animal_dict['name'])
            except Animal.DoesNotExist:
                if validated:
                    valid_animals.append(animal_dict)
        # If we have at least 6 valid types of animals, move forward with validating quiz as a whole
        if len(valid_animals) >= 6:
            # Check to see if enough unique fields exist to generate a quiz
            unique_diets = []
            unique_locations = []
            unique_lifestyles = []
            unique_group_behaviors = []
            # First, iterate through animals and add unique fields
            for animal in valid_animals:
                # Check that it has a diet
                diet = animal['characteristics'].get('diet', None)
                if diet:
                    if diet not in unique_diets:
                        unique_diets.append(diet)
                # Check that it has a lifestyle or group_behavior
                lifestyle = animal['characteristics'].get('lifestyle', None)
                group_behavior = animal['characteristics'].get('group_behavior', None)
                if lifestyle or group_behavior:
                    # Try to add them to lists if unique
                    if lifestyle:
                        if lifestyle not in unique_lifestyles:
                            unique_lifestyles.append(lifestyle)
                    if group_behavior:
                        if group_behavior not in unique_group_behaviors:
                            unique_group_behaviors.append(group_behavior)
                # Check for unique locations
                locations = animal.get('locations', None)
                # Try to add them to locations if unique
                if locations:
                    for location in locations:
                        if location not in unique_locations:
                            unique_locations.append(location)
            # Now check that requirements are met for unique answers
            if len(unique_diets) < 2:
                raise ValidationError("Not enough diets found: unable to generate quiz.")
            if len(unique_locations) < 1:
                raise ValidationError("Not enough locations found: unable to generate quiz.")
            if len(unique_lifestyles) < 2 and len(unique_group_behaviors) < 2:
                raise ValidationError("Not enough lifestyles and group behaviors found: unable to generate quiz.")
            # Create 'answers' to return unique answer data for use in external method
            answers = {"diet": unique_diets, "location": unique_locations,
                       "lifestyle": unique_lifestyles, "group_behavior": unique_group_behaviors}
            return valid_animals, answers
        else:
            raise ValidationError("Insufficient valid animals: unable to generate quiz.")


class Question(models.Model):
    """
    A Question object holds a question string and has a one-to-many
    relationship to a Quiz
    """
    # 'category' is the type of answer this question gets (e.g. diet, thus it's a 'diet' question)
    category = models.CharField(max_length=20)
    quiz = models.ForeignKey("Quiz", related_name="questions", on_delete=models.CASCADE)


class Answer(models.Model):
    """
    An Answer object holds an answer string and has a one-to-many
    relationship to a Question
    """
    text = models.CharField(max_length=200)
    # Question is in quotes to avoid circular imports
    question = models.ForeignKey("Question", related_name="answers", on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class QuizResult(models.Model):
    responses = models.JSONField()
    animal_match = models.CharField(max_length=30, null=True, blank=True, default=None)
    score = models.IntegerField(null=True, blank=True, default=None)
    quiz = models.ForeignKey("Quiz", related_name="results", on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.animal_match

    def calculate_score(self):
        """
         This function calculates the similarity of each animal in the Animal API by calculating
         a score of similarity. The highest possible value is 5/5 if the animal is an exact match
         to the answers provided in QuizResult.responses. If multiple animals match, a random one
         is returned

         :return: score of similarity, match_name
        """
        # Set variable
        max_score = 0
        matches = {1: [], 2: [], 3: [], 4: []}
        # Iterate through the animals dict
        for animal in self.quiz.animals.all():
            # Set up variable
            temp_score = 0
            # Check if each response attribute matches the potential match's same attribute. If so, increment score
            if self.responses["location"].lower() in [location.lower() for location in animal.locations]:
                temp_score += 1
            if self.responses["diet"].lower() == animal.diet.lower():
                temp_score += 1
            if "lifestyle" in self.responses and animal.lifestyle is not None:
                if self.responses["lifestyle"].lower() == animal.lifestyle.lower():
                    temp_score += 1
            if "group_behavior" in self.responses and animal.group_behavior is not None:
                if self.responses["group_behavior"].lower() == animal.group_behavior.lower():
                    temp_score += 1
            # Add final animal score to dict with animals sorted by score
            if temp_score > 0:
                matches[temp_score].append(animal.name)
            # Check if temp_score is larger than max score, and reset accordingly
            if temp_score > max_score:
                max_score = temp_score
        # if only one highest score exists, return the animal match
        if max_score == 0:
            raise ValueError("No matches found. Could not create QuizResult with match.")
        else:
            if len(matches[max_score]) == 1:
                self.score = max_score
                self.animal_match = matches[max_score][0]
            # if multiple highest scores exist, return a random animal
            elif len(matches[max_score]) > 1:
                self.score = max_score
                self.animal_match = random.choice(matches[max_score])


class Animal(models.Model):
    name = models.CharField(max_length=50, unique=True)
    species = models.CharField(max_length=100, default=None)
    habitat = models.CharField(max_length=100)
    lifestyle = models.CharField(max_length=50, null=True, blank=True, default=None)  # Ex: Diurnal or Nocturnal
    locations = models.JSONField(default=None)
    diet = models.CharField(max_length=50)
    group_behavior = models.CharField(max_length=50, null=True, blank=True, default=None)  # Ex: Solitary or Herd
    lifespan = models.CharField(max_length=50)
    image_url = models.URLField(null=True, blank=True, default=None)
    # Attach the animal to a quiz
    quiz = models.ForeignKey("Quiz", related_name="animals", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @classmethod
    def validate_animal_data(cls, animal_data):
        """
        This method validates whether animal data for an animal (from API call) has enough
        valid fields to create the animal object
        :return: True if the animal object can be created and False otherwise
        """
        # Check that the animal has each correct field present
        verified = True
        if "habitat" not in animal_data["characteristics"]:
            verified = False
        if "locations" not in animal_data:
            verified = False
        if "diet" not in animal_data["characteristics"]:
            verified = False
        if "group_behavior" not in animal_data["characteristics"] and "lifestyle" not in animal_data["characteristics"]:
            verified = False
        if "lifespan" not in animal_data["characteristics"]:
            verified = False
        if "scientific_name" not in animal_data["taxonomy"]:
            verified = False
        return verified


class Admin(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
