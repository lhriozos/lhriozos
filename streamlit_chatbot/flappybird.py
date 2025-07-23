import streamlit as st
import random
import time

# --- Game Configuration ---
GRAVITY = 1       # How much the bird falls each "turn" - Adjusted for better fall
JUMP_STRENGTH = 4 # How much the bird jumps when flapped - Adjusted for better jump
GAME_HEIGHT = 15  # The vertical height of our game world (simulated) - Adjusted for clearer view
PIPE_WIDTH = 2    # How wide the "pipe" obstacle is visually
PIPE_GAP_HEIGHT = 5 # How big the gap in the pipes is

# --- Initialize Game State in Session State ---
if 'bird_position' not in st.session_state:
    st.session_state.bird_position = GAME_HEIGHT // 2
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.pipe_position = GAME_HEIGHT # Pipe starts off-screen right
    st.session_state.pipe_gap_start = random.randint(1, GAME_HEIGHT - PIPE_GAP_HEIGHT - 1)
    st.session_state.game_started = False
    st.session_state.flap_triggered = False # Flag to indicate a flap needs to happen

# --- Game Logic Functions ---
def reset_game():
    st.session_state.bird_position = GAME_HEIGHT // 2
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.pipe_position = GAME_HEIGHT
    st.session_state.pipe_gap_start = random.randint(1, GAME_HEIGHT - PIPE_GAP_HEIGHT - 1)
    st.session_state.game_started = False
    st.session_state.flap_triggered = False

def flap_action():
    if not st.session_state.game_over:
        st.session_state.bird_position += JUMP_STRENGTH
        # Prevent bird from going above the top of the screen
        if st.session_state.bird_position >= GAME_HEIGHT: # Use >= for boundary
            st.session_state.bird_position = GAME_HEIGHT - 1
        st.session_state.game_started = True
    st.session_state.flap_triggered = False # Reset the flag immediately after action

def advance_game_state():
    if not st.session_state.game_over and st.session_state.game_started:
        # Apply gravity
        st.session_state.bird_position -= GRAVITY
        if st.session_state.bird_position < 0:
            st.session_state.bird_position = 0 # Bird hits bottom
            st.session_state.game_over = True

        # Move pipe
        st.session_state.pipe_position -= 1

        # If pipe goes off-screen, reset and increase score
        if st.session_state.pipe_position < -PIPE_WIDTH: # Ensure it clears entirely
            st.session_state.score += 1
            st.session_state.pipe_position = GAME_HEIGHT # Reset pipe far right
            st.session_state.pipe_gap_start = random.randint(1, GAME_HEIGHT - PIPE_GAP_HEIGHT - 1)

        # Collision detection (Simplified: bird is "at" pipe's x-coordinate)
        # Bird is at conceptual x=0. Pipe needs to be at x=0 or x=1 to collide
        if st.session_state.pipe_position < PIPE_WIDTH and st.session_state.pipe_position >= 0:
            # Check if bird is OUTSIDE the gap
            if (st.session_state.bird_position < st.session_state.pipe_gap_start or
                st.session_state.bird_position >= st.session_state.pipe_gap_start + PIPE_GAP_HEIGHT):
                st.session_state.game_over = True

# --- Streamlit UI ---
st.set_page_config(layout="centered") # Use centered layout for better game view

st.title("🐦 Flappy Bird (Simplified Streamlit Edition)")

# JavaScript to trigger a hidden button on spacebar press
st.markdown("""
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    if (e.code === 'Space') {
        const buttons = Array.from(doc.querySelectorAll('button'));
        for (let i = 0; i < buttons.length; i++) {
            if (buttons[i].innerText === 'FLAP_TRIGGER') { // Match the hidden button's text
                buttons[i].click();
                e.preventDefault(); // Prevent default spacebar action (e.g., scrolling)
                break;
            }
        }
    }
});
</script>
""", unsafe_allow_html=True)

# This hidden button will be triggered by the JavaScript
# We use a unique string like "FLAP_TRIGGER" that the JS looks for.
# This button's text will not be visible to the user thanks to its styling in the markdown.
# The on_click should set a flag to perform the flap action on the next rerun.
if st.button("FLAP_TRIGGER", key="hidden_flap_button", on_click=lambda: st.session_state.update(flap_triggered=True)):
    pass # This button itself does nothing visible, it just sets the flag

st.markdown(
    """
    <style>
    /* Hide the actual button for 'FLAP_TRIGGER' text */
    button[data-testid="stButton"] > div > p {
        display: none;
    }
    button[data-testid="stButton"] {
        background-color: transparent;
        border: none;
        color: transparent;
        cursor: default;
        position: absolute; /* Take it out of flow */
        left: -9999px; /* Move it far away */
    }
    </style>
    """, unsafe_allow_html=True
)

if st.session_state.game_over:
    st.error(f"GAME OVER! Your final score: {st.session_state.score}")
    st.button("Play Again", on_click=reset_game)
else:
    st.sidebar.markdown("### Controls")
    # A visible button for testing or if spacebar fails
    st.sidebar.button("🚀 Click to Flap!", on_click=flap_action)
    st.sidebar.write("---")
    st.sidebar.write("Press **Spacebar** or click 'Click to Flap!' to make the bird jump.")
    st.sidebar.write("Avoid the pipes and don't hit the top or bottom!")
    st.sidebar.write("Your goal is to get the highest score.")

    st.subheader(f"Score: {st.session_state.score}")

    # Display game board
    board = []
    # Loop from top (GAME_HEIGHT-1) down to 0
    for y in range(GAME_HEIGHT - 1, -1, -1):
        row = []
        # A conceptual width for display, simplified for text
        for x in range(GAME_HEIGHT // 2 + PIPE_WIDTH + 1): # Adjust width to show pipes approaching
            if x == 0 and y == st.session_state.bird_position:
                row.append("🐦") # Bird
            elif x == st.session_state.pipe_position: # Pipe front
                if y < st.session_state.pipe_gap_start or y >= st.session_state.pipe_gap_start + PIPE_GAP_HEIGHT:
                    row.append("🔲") # Pipe wall
                else:
                    row.append("  ") # Pipe gap
            elif x == st.session_state.pipe_position + 1 and PIPE_WIDTH > 1: # Pipe back (if width > 1)
                 if y < st.session_state.pipe_gap_start or y >= st.session_state.pipe_gap_start + PIPE_GAP_HEIGHT:
                    row.append("🔲") # Pipe wall
                 else:
                    row.append("  ") # Pipe gap
            else:
                row.append("  ") # Empty space
        board.append(" ".join(row))

    # Using st.text for preformatted text output
    st.text("\n".join(board))

    # If game started and not over, advance state and rerun
    if st.session_state.game_started and not st.session_state.game_over:
        if st.session_state.flap_triggered: # Only flap if spacebar was pressed
            flap_action()
        advance_game_state()
        time.sleep(0.2) # Adjusted sleep for smoother animation (feel free to tweak)
        st.rerun() # Use st.rerun() directly

    elif not st.session_state.game_started and not st.session_state.game_over:
        st.info("Press **Spacebar** or click 'Click to Flap!' to start the game!")