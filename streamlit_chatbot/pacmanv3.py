import streamlit as st
import random

# Game settings
grid_size = 8
num_dots = 10
start_pos = [1, 1]
walls = [[0, 2], [2, 0], [4, 2], [5, 5], [6, 3], [3, 6]]  # Add more walls if you like
mob_start_positions = [[7, 7], [0, 7]]  # Starting positions for mobs
max_lives = 3

# Function to generate random dots
def generate_dots():
    all_positions = [
        [i, j]
        for i in range(grid_size)
        for j in range(grid_size)
        if [i, j] != start_pos and [i, j] not in walls and [i, j] not in mob_start_positions
    ]
    return random.sample(all_positions, num_dots)

# Initialize state
if "pacman_pos" not in st.session_state:
    st.session_state.pacman_pos = start_pos.copy()
if "dots" not in st.session_state:
    st.session_state.dots = generate_dots()
if "score" not in st.session_state:
    st.session_state.score = 0
if "won" not in st.session_state:
    st.session_state.won = False
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "mobs" not in st.session_state:
    st.session_state.mobs = mob_start_positions.copy()
if "lives" not in st.session_state:
    st.session_state.lives = max_lives

# Movement logic for mobs
def move_mobs():
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (1, -1), (-1, 1), (-1, -1), (-2, 0), (2, 0), (0, -2), (0, 2), (2, 2), (2, -2), (-2, 2), (-2, -2)]  # up, down, left, right, diagonal
    new_mobs = []
    for mob_pos in st.session_state.mobs:
        random.shuffle(directions)
        moved = False
        for dx, dy in directions:
            new_x = mob_pos[0] + dx
            new_y = mob_pos[1] + dy
            # Avoid walls, grid boundaries, and other mobs
            if (
                0 <= new_x < grid_size
                and 0 <= new_y < grid_size
                and [new_x, new_y] not in walls
                and [new_x, new_y] not in new_mobs
            ):
                new_mobs.append([new_x, new_y])
                moved = True
                break
        if not moved:
            new_mobs.append(mob_pos)  # stay put if no valid moves
    st.session_state.mobs = new_mobs

# Pac-Man movement
def move(dx, dy):
    if st.session_state.won or st.session_state.game_over:
        return

    new_x = st.session_state.pacman_pos[0] + dx
    new_y = st.session_state.pacman_pos[1] + dy
    if 0 <= new_x < grid_size and 0 <= new_y < grid_size and [new_x, new_y] not in walls:
        st.session_state.pacman_pos = [new_x, new_y]
        if [new_x, new_y] in st.session_state.dots:
            st.session_state.dots.remove([new_x, new_y])
            st.session_state.score += 10
            if len(st.session_state.dots) == 0:
                st.session_state.won = True

        # Move mobs after Pac-Man moves
        move_mobs()

        # Check if mobs caught Pac-Man
        if st.session_state.pacman_pos in st.session_state.mobs:
            st.session_state.lives -= 1
            if st.session_state.lives <= 0:
                st.session_state.game_over = True
            else:
                # Reset Pac-Man and mobs positions but keep score/dots/lives
                st.session_state.pacman_pos = start_pos.copy()
                st.session_state.mobs = mob_start_positions.copy()

# Title
st.title("🟡 Pac-Man Streamlit – Lives Edition with Mobs")

# Control buttons
col1, col2, col3 = st.columns(3)
with col2:
    if st.button("⬆️"):
        move(-1, 0)
with col1:
    if st.button("⬅️"):
        move(0, -1)
with col3:
    if st.button("➡️"):
        move(0, 1)
with col2:
    if st.button("⬇️"):
        move(1, 0)

# Draw the grid
for i in range(grid_size):
    row = ""
    for j in range(grid_size):
        pos = [i, j]
        if pos == st.session_state.pacman_pos:
            row += "🟡 "
        elif pos in st.session_state.mobs:
            row += "👾 "
        elif pos in walls:
            row += "🟥 "
        elif pos in st.session_state.dots:
            row += "• "
        else:
            row += "⬛ "
    st.markdown(row)

# Display score and lives
st.success(f"Score: {st.session_state.score} | Lives: {st.session_state.lives}")

# Messages
if st.session_state.won:
    st.balloons()
    st.markdown("🎉 You win! All the dots are gone!")
elif st.session_state.game_over:
    st.error("💀 Game Over! You ran out of lives.")

# Restart button
if st.button("Restart Game"):
    st.session_state.pacman_pos = start_pos.copy()
    st.session_state.dots = generate_dots()
    st.session_state.score = 0
    st.session_state.won = False
    st.session_state.game_over = False
    st.session_state.mobs = mob_start_positions.copy()
    st.session_state.lives = max_lives