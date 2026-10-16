import random
import streamlit as st

st.set_page_config(
    page_title="Pixelmon Adventure",
    page_icon="⚡",
    layout="wide"
)

POKEMON = {
    "Pikachu": {"emoji": "⚡", "hp": 100, "attack": 24},
    "Charmander": {"emoji": "🔥", "hp": 110, "attack": 27},
    "Bulbasaur": {"emoji": "🌿", "hp": 120, "attack": 22},
    "Squirtle": {"emoji": "💧", "hp": 130, "attack": 20},
}

WILD = {
    "Pikachu": "⚡",
    "Charmander": "🔥",
    "Bulbasaur": "🌿",
    "Squirtle": "💧",
    "Eevee": "🦊",
    "Snorlax": "💤",
}

def init_game():
    defaults = {
        "started": False,
        "pokemon": "Pikachu",
        "level": 1,
        "exp": 0,
        "coins": 0,
        "hp": 100,
        "x": 5,
        "y": 3,
        "enemy": None,
        "boss": None,
        "team": [],
        "message": "Chào mừng đến Pixelmon Adventure!",
        "world_seed": random.randint(1, 999999),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_game()

def say(message):
    st.session_state.message = message

def max_hp():
    base = POKEMON[st.session_state.pokemon]["hp"]
    return base + (st.session_state.level - 1) * 20

def gain_exp(amount):
    st.session_state.exp += amount
    while st.session_state.exp >= st.session_state.level * 100:
        st.session_state.exp -= st.session_state.level * 100
        st.session_state.level += 1
        st.session_state.hp = max_hp()
        say(f"🌟 LÊN CẤP {st.session_state.level}! HP đã hồi phục!")

def move(dx, dy):
    st.session_state.x = max(
        0, min(11, st.session_state.x + dx)
    )
    st.session_state.y = max(
        0, min(7, st.session_state.y + dy)
    )

    if st.session_state.boss:
        say("👹 Boss đang xuất hiện! Hãy chiến đấu!")
        return

    if not st.session_state.enemy and random.random() < 0.35:
        name = random.choice(list(WILD.keys()))
        hp = random.randint(45, 85)
        st.session_state.enemy = {
            "name": name,
            "hp": hp,
            "max": hp,
        }
        say(f"🌱 Một Pokémon hoang dã xuất hiện: {name}!")
    else:
        say("Bạn đang khám phá thế giới Pixelmon!")

def enemy_attack():
    if not st.session_state.enemy and not st.session_state.boss:
        return

    damage = random.randint(8, 18)
    if st.session_state.boss:
        damage = random.randint(18, 30)

    st.session_state.hp -= damage

    if st.session_state.hp <= 0:
        st.session_state.hp = max(1, max_hp() // 2)
        st.session_state.x = 5
        st.session_state.y = 3
        say("💫 Bạn đã thua trận và trở về điểm hồi sinh!")
    else:
        say(f"💥 Đối thủ phản công, gây {damage} sát thương!")

def attack(power=1):
    target = st.session_state.boss or st.session_state.enemy

    if not target:
        say("Hãy di chuyển để tìm Pokémon hoặc triệu hồi Boss!")
        return

    base = POKEMON[st.session_state.pokemon]["attack"]
    damage = base + st.session_state.level * 3

    if power == 2:
        damage *= 2

    target["hp"] -= damage
    name = target["name"] if "name" in target else "Boss"

    if target["hp"] <= 0:
        if st.session_state.boss:
            st.session_state.boss = None
            st.session_state.coins += 100
            gain_exp(100)
            say("🏆 Hạ gục Boss! Bạn nhận 100 xu và 100 EXP!")
        else:
            st.session_state.enemy = None
            st.session_state.coins += 10
            gain_exp(20)
            say(f"🎉 Bạn đã đánh bại {name}! +10 xu, +20 EXP.")
        return

    say(f"✨ Bạn gây {damage} sát thương lên {name}!")
    enemy_attack()

def heal():
    st.session_state.hp = min(max_hp(), st.session_state.hp + 35)
    say("💚 Bạn đã hồi phục tối đa 35 HP!")

def catch():
    enemy = st.session_state.enemy

    if not enemy:
        say("Bạn chưa gặp Pokémon hoang dã!")
        return

    if random.random() < 0.65 or enemy["hp"] <= enemy["max"] * 0.3:
        name = enemy["name"]
        st.session_state.team.append(name)
        st.session_state.coins += 5
        st.session_state.enemy = None
        say(f"🔴 Thu phục thành công {name}! +5 xu.")
    else:
        say("Pokémon đã thoát! Hãy làm yếu nó rồi thử lại.")

def spawn_boss():
    if st.session_state.boss:
        say("Boss đã xuất hiện rồi!")
        return

    hp = 350 + st.session_state.level * 50
    st.session_state.boss = {
        "name": "Boss Pixelmon",
        "hp": hp,
        "max": hp,
    }
    st.session_state.enemy = None
    say("⚠️ BOSS PIXELMON xuất hiện! Hãy chuẩn bị chiến đấu!")

def save_game():
    data = {
        "pokemon": st.session_state.pokemon,
        "level": st.session_state.level,
        "exp": st.session_state.exp,
        "coins": st.session_state.coins,
        "hp": st.session_state.hp,
        "x": st.session_state.x,
        "y": st.session_state.y,
        "team": st.session_state.team,
    }
    st.session_state["saved_game"] = data
    say("💾 Đã lưu dữ liệu trong phiên chơi hiện tại!")

def load_game():
    data = st.session_state.get("saved_game")
    if not data:
        say("Chưa có bản lưu trong phiên này!")
        return

    for key, value in data.items():
        st.session_state[key] = value
    say("📂 Đã tải bản lưu!")

st.title("⚡ Pixelmon Adventure")
st.caption("Fan-made game • Python + Streamlit")

if not st.session_state.started:
    st.subheader("🎮 Chọn Pokémon khởi đầu")

    cols = st.columns(4)
    names = list(POKEMON.keys())

    for i, name in enumerate(names):
        with cols[i]:
            st.markdown(f"## {POKEMON[name]['emoji']}")
            st.write(name)
            if st.button("Chọn " + name, key="pick_" + name):
                st.session_state.pokemon = name
                st.session_state.hp = POKEMON[name]["hp"]
                st.session_state.started = True
                st.rerun()

    st.stop()

# Thanh thông tin
c1, c2, c3, c4 = st.columns(4)
c1.metric("Cấp độ", st.session_state.level)
c2.metric("EXP", st.session_state.exp)
c3.metric("Xu", st.session_state.coins)
c4.metric("Đội Pokémon", len(st.session_state.team) + 1)

st.subheader("❤️ Pokémon của bạn")
st.write(
    f"{POKEMON[st.session_state.pokemon]['emoji']} "
    f"**{st.session_state.pokemon}**"
)
st.progress(max(0, st.session_state.hp / max_hp()))
st.write(f"HP: {st.session_state.hp}/{max_hp()}")

st.divider()
st.subheader("🗺️ Bản đồ khám phá")

# Bản đồ 12 x 8
random.seed(st.session_state.world_seed)
terrain = {}
for yy in range(8):
    for xx in range(12):
        terrain[(xx, yy)] = random.choices(
            ["🌱", "🌳", "🌼", "💧"],
            weights=[65, 18, 12, 5]
        )[0]

for yy in range(8):
    cols = st.columns(12)
    for xx in range(12):
        if xx == st.session_state.x and yy == st.session_state.y:
            symbol = "🧢"
        elif st.session_state.boss and xx == 10 and yy == 6:
            symbol = "👹"
        else:
            symbol = terrain[(xx, yy)]

        cols[xx].markdown(
            f"<div style='text-align:center;"
            f"font-size:22px;background:#203a2b;"
            f"border-radius:5px;padding:5px 0'>"
            f"{symbol}</div>",
            unsafe_allow_html=True,
        )

st.caption("🧢 Bạn • 🌱 Cỏ • 🌳 Cây • 🌼 Hoa • 💧 Nước • 👹 Boss")

# Điều khiển
st.subheader("🕹️ Điều khiển")
a, b, c = st.columns(3)

with b:
    if st.button("⬆️ Đi lên", use_container_width=True):
        move(0, -1)
        st.rerun()

a, b, c = st.columns(3)

with a:
    if st.button("⬅️ Sang trái", use_container_width=True):
        move(-1, 0)
        st.rerun()

with b:
    if st.button("⬇️ Đi xuống", use_container_width=True):
        move(0, 1)
        st.rerun()

with c:
    if st.button("➡️ Sang phải", use_container_width=True):
        move(1, 0)
        st.rerun()

st.divider()
st.subheader("⚔️ Chiến đấu")

enemy = st.session_state.enemy
boss = st.session_state.boss

if enemy:
    st.warning(f"Hoang dã: {enemy['name']}")
    st.progress(max(0, enemy["hp"] / enemy["max"]))
    st.write(f"HP: {max(0, enemy['hp'])}/{enemy['max']}")
elif boss:
    st.error("👹 BOSS PIXELMON")
    st.progress(max(0, boss["hp"] / boss["max"]))
    st.write(f"Boss HP: {max(0, boss['hp'])}/{boss['max']}")
else:
    st.info("Chưa có đối thủ. Hãy khám phá hoặc gọi Boss!")

a, b, c, d = st.columns(4)

with a:
    if st.button("⚡ Tấn công", use_container_width=True):
        attack(1)
        st.rerun()

with b:
    if st.button("💥 Siêu kỹ năng", use_container_width=True):
        attack(2)
        st.rerun()

with c:
    if st.button("💚 Hồi máu", use_container_width=True):
        heal()
        st.rerun()

with d:
    if st.button("🔴 Thu phục", use_container_width=True):
        catch()
        st.rerun()

a, b, c = st.columns(3)

with a:
    if st.button("👹 Triệu hồi Boss", use_container_width=True):
        spawn_boss()
        st.rerun()

with b:
    if st.button("💾 Lưu tiến trình", use_container_width=True):
        save_game()
        st.rerun()

with c:
    if st.button("📂 Tải bản lưu", use_container_width=True):
        load_game()
        st.rerun()

st.subheader("🎒 Đội Pokémon")
if st.session_state.team:
    st.write(" • ".join(st.session_state.team))
else:
    st.write("Bạn chưa thu phục Pokémon nào.")

st.info(st.session_state.message)

with st.expander("🔄 Đổi Pokémon đang sử dụng"):
    options = list(POKEMON.keys())
    selected = st.selectbox(
        "Chọn Pokémon",
        options,
        index=options.index(st.session_state.pokemon),
    )
    if st.button("Đổi Pokémon"):
        st.session_state.pokemon = selected
        st.session_state.hp = max_hp()
        say(f"Bạn đã chuyển sang {selected}!")
        st.rerun()
    
