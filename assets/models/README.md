When adding a new character model, ensure that:
- .obj is added to assets/models
- texture is added to assets/maps and assets/graphics
- import in target file is updated to match .obj name
- glTexImage2D() is updated to reflect the texture dimensions
- The model itself is centered at the origin (0, x, 0) for correct camera movement