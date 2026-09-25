# Level 0

Each paint group below has a colour, an opacity, a binary inclusion mask (1 if the point lies inside it, 0 if it is excluded), and optional isolation and knockout rules. Children are composited source-over onto the backdrop of their group; an isolated group starts its children over a transparent backdrop and only then blends onto the inherited one, while a non-isolated group's children keep compositing onto the inherited backdrop; a knockout group paints each child onto the group's own base rather than onto its siblings, so the latest painted child remains and coverage is the maximum of its children. Coverage is the fraction of the point painted, 0..1.
g1: leaf alpha=0.434 color=(0.258, 0.448, 0.112) mask=0
g101: leaf alpha=0.214 color=(0.433, 0.967, 0.21) mask=0
These groups are composited in order over an opaque black background. Report the final colour as R,G,B (0..1), the alpha (0..1) and the coverage (0..1) at the point, as `R,G,B,A,Coverage`. The answer is one tuple of five numbers.

Answer: 0.0,0.0,0.0,1.0,1.0

Each paint group below has a colour, an opacity, a binary inclusion mask (1 if the point lies inside it, 0 if it is excluded), and optional isolation and knockout rules. Children are composited source-over onto the backdrop of their group; an isolated group starts its children over a transparent backdrop and only then blends onto the inherited one, while a non-isolated group's children keep compositing onto the inherited backdrop; a knockout group paints each child onto the group's own base rather than onto its siblings, so the latest painted child remains and coverage is the maximum of its children. Coverage is the fraction of the point painted, 0..1.
g1: leaf alpha=0.235 color=(0.563, 0.7, 0.774) mask=0
g101: leaf alpha=0.592 color=(0.828, 0.154, 0.592) mask=0
These groups are composited in order over an opaque black background. Report the final colour as R,G,B (0..1), the alpha (0..1) and the coverage (0..1) at the point, as `R,G,B,A,Coverage`. The answer is one tuple of five numbers.

Answer: 0.0,0.0,0.0,1.0,1.0

# Level 2

Each paint group below has a colour, an opacity, a binary inclusion mask (1 if the point lies inside it, 0 if it is excluded), and optional isolation and knockout rules. Children are composited source-over onto the backdrop of their group; an isolated group starts its children over a transparent backdrop and only then blends onto the inherited one, while a non-isolated group's children keep compositing onto the inherited backdrop; a knockout group paints each child onto the group's own base rather than onto its siblings, so the latest painted child remains and coverage is the maximum of its children. Coverage is the fraction of the point painted, 0..1.
g1: group alpha=0.85 isolated=False knockout=False
  g10: leaf alpha=0.578 color=(0.572, 0.8, 0.463) mask=1
  g11: leaf alpha=0.393 color=(0.16, 0.497, 0.244) mask=1
g101: group alpha=0.731 isolated=True knockout=True
  g1010: leaf alpha=0.421 color=(0.183, 0.362, 0.069) mask=0
  g1011: leaf alpha=0.448 color=(0.696, 0.91, 0.428) mask=0
g201: group alpha=0.654 isolated=True knockout=False
  g2010: leaf alpha=0.953 color=(0.086, 0.725, 0.872) mask=1
  g2011: leaf alpha=0.535 color=(0.48, 0.835, 0.223) mask=1
These groups are composited in order over an opaque black background. Report the final colour as R,G,B (0..1), the alpha (0..1) and the coverage (0..1) at the point, as `R,G,B,A,Coverage`. The answer is one tuple of five numbers.

Answer: 0.274,0.648,0.41,1.0,1.0

Each paint group below has a colour, an opacity, a binary inclusion mask (1 if the point lies inside it, 0 if it is excluded), and optional isolation and knockout rules. Children are composited source-over onto the backdrop of their group; an isolated group starts its children over a transparent backdrop and only then blends onto the inherited one, while a non-isolated group's children keep compositing onto the inherited backdrop; a knockout group paints each child onto the group's own base rather than onto its siblings, so the latest painted child remains and coverage is the maximum of its children. Coverage is the fraction of the point painted, 0..1.
g1: group alpha=0.322 isolated=True knockout=True
  g10: leaf alpha=0.744 color=(0.477, 0.803, 0.303) mask=0
  g11: leaf alpha=0.729 color=(0.177, 0.496, 0.857) mask=1
g101: group alpha=0.868 isolated=False knockout=True
  g1010: leaf alpha=0.956 color=(0.819, 0.923, 0.941) mask=0
  g1011: leaf alpha=0.254 color=(0.42, 0.591, 0.948) mask=1
g201: group alpha=0.768 isolated=False knockout=True
  g2010: leaf alpha=0.629 color=(0.261, 0.036, 0.793) mask=1
  g2011: leaf alpha=0.876 color=(0.251, 0.54, 0.414) mask=0
These groups are composited in order over an opaque black background. Report the final colour as R,G,B (0..1), the alpha (0..1) and the coverage (0..1) at the point, as `R,G,B,A,Coverage`. The answer is one tuple of five numbers.

Answer: 0.191,0.132,0.572,1.0,1.0

# Level 5

Each paint group below has a colour, an opacity, a binary inclusion mask (1 if the point lies inside it, 0 if it is excluded), and optional isolation and knockout rules. Children are composited source-over onto the backdrop of their group; an isolated group starts its children over a transparent backdrop and only then blends onto the inherited one, while a non-isolated group's children keep compositing onto the inherited backdrop; a knockout group paints each child onto the group's own base rather than onto its siblings, so the latest painted child remains and coverage is the maximum of its children. Coverage is the fraction of the point painted, 0..1.
g1: group alpha=0.693 isolated=False knockout=True
  g10: group alpha=0.929 isolated=True knockout=False
    g100: leaf alpha=0.569 color=(0.747, 0.842, 0.201) mask=1
    g101: leaf alpha=0.723 color=(0.08, 0.504, 0.451) mask=0
  g11: group alpha=0.559 isolated=False knockout=False
    g110: leaf alpha=0.741 color=(0.677, 0.028, 0.637) mask=0
    g111: leaf alpha=0.327 color=(0.07, 0.329, 0.408) mask=0
g101: group alpha=0.483 isolated=True knockout=False
  g1010: group alpha=0.809 isolated=False knockout=False
    g10100: leaf alpha=0.26 color=(0.327, 0.014, 0.974) mask=0
    g10101: leaf alpha=0.219 color=(0.259, 0.658, 0.273) mask=1
  g1011: group alpha=0.994 isolated=False knockout=True
    g10110: leaf alpha=0.995 color=(0.813, 0.673, 0.264) mask=1
    g10111: leaf alpha=0.922 color=(0.426, 0.817, 0.819) mask=1
g201: group alpha=0.625 isolated=True knockout=True
  g2010: group alpha=0.324 isolated=False knockout=True
    g20100: leaf alpha=0.712 color=(0.351, 0.314, 0.363) mask=1
    g20101: leaf alpha=0.343 color=(0.586, 0.052, 0.889) mask=0
  g2011: group alpha=0.551 isolated=False knockout=False
    g20110: leaf alpha=0.969 color=(0.816, 0.127, 0.303) mask=1
    g20111: leaf alpha=0.937 color=(0.855, 0.261, 0.564) mask=1
g301: group alpha=0.341 isolated=False knockout=False
  g3010: group alpha=0.999 isolated=False knockout=True
    g30100: leaf alpha=0.505 color=(0.021, 0.591, 0.219) mask=0
    g30101: leaf alpha=0.322 color=(0.782, 0.747, 0.433) mask=1
  g3011: group alpha=0.645 isolated=False knockout=False
    g30110: leaf alpha=0.424 color=(0.843, 0.087, 0.13) mask=1
    g30111: leaf alpha=0.922 color=(0.745, 0.305, 0.299) mask=1
These groups are composited in order over an opaque black background. Report the final colour as R,G,B (0..1), the alpha (0..1) and the coverage (0..1) at the point, as `R,G,B,A,Coverage`. The answer is one tuple of five numbers.

Answer: 0.577,0.422,0.419,1.0,1.0

Each paint group below has a colour, an opacity, a binary inclusion mask (1 if the point lies inside it, 0 if it is excluded), and optional isolation and knockout rules. Children are composited source-over onto the backdrop of their group; an isolated group starts its children over a transparent backdrop and only then blends onto the inherited one, while a non-isolated group's children keep compositing onto the inherited backdrop; a knockout group paints each child onto the group's own base rather than onto its siblings, so the latest painted child remains and coverage is the maximum of its children. Coverage is the fraction of the point painted, 0..1.
g1: group alpha=0.884 isolated=False knockout=False
  g10: group alpha=0.939 isolated=True knockout=True
    g100: leaf alpha=0.288 color=(0.016, 0.34, 0.636) mask=1
    g101: leaf alpha=0.976 color=(0.188, 0.093, 0.83) mask=1
  g11: group alpha=0.448 isolated=False knockout=True
    g110: leaf alpha=0.802 color=(0.866, 0.483, 0.761) mask=1
    g111: leaf alpha=0.653 color=(0.015, 0.278, 0.807) mask=0
g101: group alpha=0.669 isolated=False knockout=True
  g1010: group alpha=0.777 isolated=True knockout=True
    g10100: leaf alpha=0.404 color=(0.477, 0.665, 0.329) mask=0
    g10101: leaf alpha=0.732 color=(0.799, 0.717, 0.302) mask=1
  g1011: group alpha=0.736 isolated=False knockout=False
    g10110: leaf alpha=0.984 color=(0.909, 0.722, 0.789) mask=1
    g10111: leaf alpha=0.851 color=(0.835, 0.367, 0.323) mask=0
g201: group alpha=0.817 isolated=True knockout=True
  g2010: group alpha=0.545 isolated=True knockout=True
    g20100: leaf alpha=0.913 color=(0.461, 0.792, 0.342) mask=1
    g20101: leaf alpha=0.22 color=(0.634, 0.715, 0.069) mask=1
  g2011: group alpha=0.545 isolated=False knockout=True
    g20110: leaf alpha=0.254 color=(0.227, 0.435, 0.369) mask=1
    g20111: leaf alpha=0.395 color=(0.629, 0.178, 0.934) mask=0
g301: group alpha=0.813 isolated=True knockout=False
  g3010: group alpha=0.662 isolated=False knockout=True
    g30100: leaf alpha=0.432 color=(0.014, 0.827, 0.401) mask=1
    g30101: leaf alpha=0.648 color=(0.646, 0.702, 0.066) mask=1
  g3011: group alpha=0.874 isolated=False knockout=True
    g30110: leaf alpha=0.958 color=(0.099, 0.245, 0.782) mask=0
    g30111: leaf alpha=0.809 color=(0.172, 0.797, 0.119) mask=1
These groups are composited in order over an opaque black background. Report the final colour as R,G,B (0..1), the alpha (0..1) and the coverage (0..1) at the point, as `R,G,B,A,Coverage`. The answer is one tuple of five numbers.

Answer: 0.354,0.676,0.297,1.0,1.0
