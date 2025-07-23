import streamlit as st
import random

# Game settings
grid_size = 12
num_dots = 20
num_pellets = 3
start_pos = [1, 1]
ghost_start_positions = [[10, 10], [10, 1], [1, 10], [6, 6]]
walls = [[0, 2], [2, 0], [4, 2], [5, 5], [6, 3], [3, 6], [7, 7], [8, 4], [2, 9]]

# Function to generate random dots
def generate_dots():
    all_positions = [
        [i, j]
        for i in range(grid_size)
        for j in range(grid_size)
        if [i, j] != start_pos and [i, j] not in walls
    ]
    return random.sample(all_positions, num_dots)

# Function to generate random pellet positions
def generate_power_pellets():
    valid_positions = [
        [i, j]
        for i in range(grid_size)
        for j in range(grid_size)
        if [i, j] != start_pos and [i, j] not in walls
    ]
    return random.sample(valid_positions, num_pellets)

# Initialize state
if "pacman_pos" not in st.session_state:
    st.session_state.pacman_pos = start_pos.copy()
if "dots" not in st.session_state:
    st.session_state.dots = generate_dots()
if "score" not in st.session_state:
    st.session_state.score = 0
if "won" not in st.session_state:
    st.session_state.won = False
if "lives" not in st.session_state:
    st.session_state.lives = 3
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "power_pellets" not in st.session_state:
    st.session_state.power_pellets = generate_power_pellets()
if "ghosts_vulnerable" not in st.session_state:
    st.session_state.ghosts_vulnerable = False
if "vulnerable_timer" not in st.session_state:
    st.session_state.vulnerable_timer = 0
if "life_lost" not in st.session_state:
    st.session_state.life_lost = False
if "move_count" not in st.session_state:
    st.session_state.move_count = 0

# Ghosts
for i in range(4):
    key = f"ghost{i+1}"
    if key not in st.session_state:
        st.session_state[key] = ghost_start_positions[i].copy()

# Movement logic
def move(dx, dy):
    if st.session_state.won or st.session_state.game_over:
        return

    st.session_state.move_count += 1
    new_x = st.session_state.pacman_pos[0] + dx
    new_y = st.session_state.pacman_pos[1] + dy
    if 0 <= new_x < grid_size and 0 <= new_y < grid_size and [new_x, new_y] not in walls:
        st.session_state.pacman_pos = [new_x, new_y]
        if [new_x, new_y] in st.session_state.dots:
            st.session_state.dots.remove([new_x, new_y])
            st.session_state.score += 10
            if len(st.session_state.dots) == 0:
                st.session_state.won = True
        if [new_x, new_y] in st.session_state.power_pellets:
            st.session_state.power_pellets.remove([new_x, new_y])
            st.session_state.ghosts_vulnerable = True
            st.session_state.vulnerable_timer = 10

    # Move ghosts every 2 Pac-Man moves
    if st.session_state.move_count % 2 == 0:
        for i in range(4):
            move_ghost(f"ghost{i+1}")
        check_ghost_collision()  # ✅ Ghost moving into Pac-Man

    # Decrease vulnerable timer
    if st.session_state.ghosts_vulnerable:
        st.session_state.vulnerable_timer -= 1
        if st.session_state.vulnerable_timer <= 0:
            st.session_state.ghosts_vulnerable = False

    # Check if Pac-Man moved into a ghost
    check_ghost_collision()

def move_ghost(key):
    ghost_pos = st.session_state[key]
    pac_pos = st.session_state.pacman_pos
    best_move = ghost_pos
    min_distance = float("inf")
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        new_x, new_y = ghost_pos[0]+dx, ghost_pos[1]+dy
        if 0 <= new_x < grid_size and 0 <= new_y < grid_size and [new_x, new_y] not in walls:
            dist = abs(new_x - pac_pos[0]) + abs(new_y - pac_pos[1])
            if dist < min_distance:
                min_distance = dist
                best_move = [new_x, new_y]
    st.session_state[key] = best_move

def check_ghost_collision():
    if st.session_state.game_over:
        return
    pac_pos = st.session_state.pacman_pos
    for i in range(4):
        key = f"ghost{i+1}"
        if st.session_state[key] == pac_pos:
            if st.session_state.ghosts_vulnerable:
                st.session_state.score += 100
                st.session_state[key] = ghost_start_positions[i]
            else:
                st.session_state.lives -= 1
                st.session_state.life_lost = True
                if st.session_state.lives <= 0:
                    st.session_state.lives = 0
                    st.session_state.game_over = True
                st.session_state.pacman_pos = start_pos.copy()

# Title
st.title("🟡 Pac-Man Streamlit – With Ghosts & Power Pellets")

# Controls
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

# Grid
for i in range(grid_size):
    row = ""
    for j in range(grid_size):
        pos = [i, j]
        if pos == st.session_state.pacman_pos:
            row += "🟡 "
        elif pos in walls:
            row += "🟥 "
        elif pos in st.session_state.dots:
            row += "🍩 "
        elif pos in st.session_state.power_pellets:
            row += "🦾 "
        elif pos in [st.session_state[f"ghost{k+1}"] for k in range(4)]:
            row += "👻 " if not st.session_state.ghosts_vulnerable else "💀 "
        else:
            row += "⬛ "
    st.markdown(row)

# Status
st.success(f"Score: {st.session_state.score} | Lives: {st.session_state.lives}")

if st.session_state.life_lost:
    st.warning("💔 You lost a life!")
    st.session_state.life_lost = False

if st.session_state.won:
    st.balloons()
    st.markdown("🎉 *You win! All the donuts are gone!*")
elif st.session_state.game_over:
    st.error("☠️ Game Over! The ghosts got you.")

# Restart
if st.button("Restart Game"):
    st.session_state.pacman_pos = start_pos.copy()
    st.session_state.dots = generate_dots()
    st.session_state.power_pellets = generate_power_pellets()
    st.session_state.score = 0
    st.session_state.lives = 3
    st.session_state.won = False
    st.session_state.game_over = False
    st.session_state.ghosts_vulnerable = False
    st.session_state.vulnerable_timer = 0
    st.session_state.move_count = 0
    for i in range(4):
        st.session_state[f"ghost{i+1}"] = ghost_start_positions[i].copy()
