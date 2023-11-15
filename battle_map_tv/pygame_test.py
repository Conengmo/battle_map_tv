import pygame
import sys


def main():
    pygame.init()

    # Set up display
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Image Display")

    image_path = r"C:\Users\frank\Downloads\Evrys Castle final.jpg"
    try:
        image = pygame.image.load(image_path)
    except pygame.error as e:
        print(f"Error loading image: {e}")
        sys.exit()

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Draw image on the screen
        screen.blit(source=image, dest=(0, 0))

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        pygame.time.Clock().tick(1000)


if __name__ == "__main__":
    main()
