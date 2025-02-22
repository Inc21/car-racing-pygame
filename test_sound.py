import pygame

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)

# Load the sound
john_deere_sound = pygame.mixer.Sound("sounds/john_deere.mp3")

# Check if the sound loaded successfully
if john_deere_sound is None:
    print("Failed to load John Deere sound.")
else:
    print("John Deere sound loaded successfully.")

# Play the sound
john_deere_sound.play()

# Keep the program running long enough to hear the sound
pygame.time.delay(5000)  # Delay for 5 seconds

# Quit Pygame
pygame.quit() 