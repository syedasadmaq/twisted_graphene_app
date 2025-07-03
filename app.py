import numpy as np
import streamlit as st
import plotly.express as px

# Parameters
a = 2.46  # graphene lattice constant in angstroms
grid_size = 400
extent = 50  # spatial extent in angstroms

# Coordinate grid
x = np.linspace(-extent, extent, grid_size)
y = np.linspace(-extent, extent, grid_size)
X, Y = np.meshgrid(x, y)

# Apply uniaxial strain to a layer
def apply_strain(X, Y, strain_percent, strain_angle_deg):
    angle_rad = np.radians(strain_angle_deg)
    strain_fraction = strain_percent / 100.0

    eps_xx = strain_fraction * np.cos(angle_rad)**2
    eps_yy = strain_fraction * np.sin(angle_rad)**2
    eps_xy = strain_fraction * np.sin(angle_rad) * np.cos(angle_rad)

    strain_matrix = np.array([
        [1 + eps_xx, eps_xy],
        [eps_xy, 1 + eps_yy]
    ])

    coords = np.stack([X, Y], axis=-1)
    strained_coords = coords @ strain_matrix.T

    X_strain = strained_coords[..., 0]
    Y_strain = strained_coords[..., 1]

    return X_strain, Y_strain

# Hexagonal lattice representation
def graphene_lattice(X, Y, a):
    lattice = np.cos(2 * np.pi * X / a)
    lattice += np.cos(2 * np.pi * (0.5 * X + (np.sqrt(3) / 2 * Y)) / a)
    lattice += np.cos(2 * np.pi * (-0.5 * X + (np.sqrt(3) / 2 * Y)) / a)
    return lattice

# Rotate grid
def rotate_grid(X, Y, angle_deg):
    angle_rad = np.radians(angle_deg)
    X_rot = X * np.cos(angle_rad) - Y * np.sin(angle_rad)
    Y_rot = X * np.sin(angle_rad) + Y * np.cos(angle_rad)
    return X_rot, Y_rot

# Streamlit App
st.title("Twisted Graphene Simulator")
st.write("Toggle between bilayer and trilayer graphene, adjust twist angles and strain interactively.")

# Mode selector
mode = st.sidebar.radio("Select Graphene System", ("Bilayer", "Trilayer"))

# Common controls
st.sidebar.header("Common Parameters")

st.sidebar.subheader("Strain for Layer 1")
strain1 = st.sidebar.slider("Strain (%)", 0.0, 10.0, 2.0, 0.1)
angle1 = st.sidebar.slider("Strain Direction (°)", 0.0, 180.0, 0.0, 1.0)

# Bilayer specific controls
if mode == "Bilayer":
    st.sidebar.header("Bilayer Settings")
    theta_layer2 = st.sidebar.slider("Twist Angle Layer 2 (°)", 0.0, 10.0, 1.5, 0.1)
    st.sidebar.subheader("Strain for Layer 2")
    strain2 = st.sidebar.slider("Strain (%)", 0.0, 10.0, 3.0, 0.1)
    angle2 = st.sidebar.slider("Strain Direction (°)", 0.0, 180.0, 30.0, 1.0)

    # Generate layers
    X1, Y1 = apply_strain(X, Y, strain1, angle1)
    X2, Y2 = apply_strain(X, Y, strain2, angle2)

    lattice1 = graphene_lattice(X1, Y1, a)
    X2_rot, Y2_rot = rotate_grid(X2, Y2, theta_layer2)
    lattice2 = graphene_lattice(X2_rot, Y2_rot, a)

    combined = lattice1 + lattice2

    title = f"Bilayer Graphene: Twist {theta_layer2}°, Strains {strain1}% / {strain2}%"

# Trilayer specific controls
else:
    st.sidebar.header("Trilayer Settings")
    theta_layer2 = st.sidebar.slider("Twist Angle Layer 2 (°)", 0.0, 10.0, 1.5, 0.1)
    theta_layer3 = st.sidebar.slider("Twist Angle Layer 3 (°)", -10.0, 10.0, -1.5, 0.1)

    st.sidebar.subheader("Strain for Layer 2")
    strain2 = st.sidebar.slider("Strain (%)", 0.0, 10.0, 3.0, 0.1)
    angle2 = st.sidebar.slider("Strain Direction (°)", 0.0, 180.0, 30.0, 1.0)

    st.sidebar.subheader("Strain for Layer 3")
    strain3 = st.sidebar.slider("Strain (%)", 0.0, 10.0, 4.0, 0.1)
    angle3 = st.sidebar.slider("Strain Direction (°)", 0.0, 180.0, 60.0, 1.0)

    # Generate layers
    X1, Y1 = apply_strain(X, Y, strain1, angle1)
    X2, Y2 = apply_strain(X, Y, strain2, angle2)
    X3, Y3 = apply_strain(X, Y, strain3, angle3)

    lattice1 = graphene_lattice(X1, Y1, a)
    X2_rot, Y2_rot = rotate_grid(X2, Y2, theta_layer2)
    lattice2 = graphene_lattice(X2_rot, Y2_rot, a)
    X3_rot, Y3_rot = rotate_grid(X3, Y3, theta_layer3)
    lattice3 = graphene_lattice(X3_rot, Y3_rot, a)

    combined = lattice1 + lattice2 + lattice3

    title = f"Trilayer Graphene: Twists {theta_layer2}° / {theta_layer3}°, Strains {strain1}% / {strain2}% / {strain3}%"

# Plot with Plotly
fig = px.imshow(
    combined,
    color_continuous_scale='Viridis',
    origin='lower',
    labels={'color': 'Intensity'},
    title=title
)
fig.update_layout(coloraxis_showscale=False)

# Show plot
st.plotly_chart(fig, use_container_width=True)