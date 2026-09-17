## Level 0

### Example 1

Prompt:

An arranger has this melody in C# major with 7 sharps: G## G C#.
Transpose the key and every note in order: up by a minor sixth (5 letter steps, 8 semitones).
Use diatonic/chromatic transposition: move letters cyclically through C D E F G A B and adjust accidentals to match the semitone shift. Natural pitch classes are C=0 D=2 E=4 F=5 G=7 A=9 B=11, modulo 12; ignore octaves. Key sharps follow F C G D A E B; flats follow B E A D G C F. In the input, a bare letter uses the source key signature; n, #, b, ##, bb mean absolute offsets 0, +1, -1, +2, -2 from the natural letter, overriding the key for that note only (no carry). Redundant courtesy accidentals change nothing. Retain each shifted letter at every stage: never substitute enharmonic letters.
Return only the final notes in input order, each with an explicit accidental including n for naturals, regardless of the final key. Format example: Gn F# Bbb.

Answer: E# En An

### Example 2

Prompt:

An arranger has this ascending major-scale fragment in Fn major with 1 flat: En Fn Gn.
Transpose the key and every note in order: up by a minor seventh (6 letter steps, 10 semitones).
Use diatonic/chromatic transposition: move letters cyclically through C D E F G A B and adjust accidentals to match the semitone shift. Natural pitch classes are C=0 D=2 E=4 F=5 G=7 A=9 B=11, modulo 12; ignore octaves. Key sharps follow F C G D A E B; flats follow B E A D G C F. In the input, a bare letter uses the source key signature; n, #, b, ##, bb mean absolute offsets 0, +1, -1, +2, -2 from the natural letter, overriding the key for that note only (no carry). Redundant courtesy accidentals change nothing. Retain each shifted letter at every stage: never substitute enharmonic letters.
The final key is major on the transposed source tonic (major offsets: 0, 2, 4, 5, 7, 9, 11). Return only its signature as 'N sharps', 'N flats', or 'no sharps or flats'; use the plural even for one. Format example: 3 flats.

Answer: 3 flats

## Level 2

### Example 1

Prompt:

An arranger has this melody in Cn major with no sharps or flats: Db B# F B Cn.
Transpose the key and every note in order: up by a major second (1 letter step, 2 semitones); then down by a minor sixth (5 letter steps, 8 semitones).
Use diatonic/chromatic transposition: move letters cyclically through C D E F G A B and adjust accidentals to match the semitone shift. Natural pitch classes are C=0 D=2 E=4 F=5 G=7 A=9 B=11, modulo 12; ignore octaves. Key sharps follow F C G D A E B; flats follow B E A D G C F. In the input, a bare letter uses the source key signature; n, #, b, ##, bb mean absolute offsets 0, +1, -1, +2, -2 from the natural letter, overriding the key for that note only (no carry). Redundant courtesy accidentals change nothing. Retain each shifted letter at every stage: never substitute enharmonic letters.
Return only the final notes in input order, each with an explicit accidental including n for naturals, regardless of the final key. Format example: Gn F# Bbb.

Answer: Gn E## Bn E# F#

### Example 2

Prompt:

An arranger has this ascending major-scale fragment in Eb major with 3 flats: C D E F G.
Transpose the key and every note in order: down by a major seventh (6 letter steps, 11 semitones); then down by a diminished fifth (4 letter steps, 6 semitones).
Use diatonic/chromatic transposition: move letters cyclically through C D E F G A B and adjust accidentals to match the semitone shift. Natural pitch classes are C=0 D=2 E=4 F=5 G=7 A=9 B=11, modulo 12; ignore octaves. Key sharps follow F C G D A E B; flats follow B E A D G C F. In the input, a bare letter uses the source key signature; n, #, b, ##, bb mean absolute offsets 0, +1, -1, +2, -2 from the natural letter, overriding the key for that note only (no carry). Redundant courtesy accidentals change nothing. Retain each shifted letter at every stage: never substitute enharmonic letters.
The final key is major on the transposed source tonic (major offsets: 0, 2, 4, 5, 7, 9, 11). Return only its signature as 'N sharps', 'N flats', or 'no sharps or flats'; use the plural even for one. Format example: 3 flats.

Answer: 2 flats

## Level 5

### Example 1

Prompt:

An arranger has this melody in Db major with 5 flats: C# F# Gn Ebb Dn F# B Cb.
Transpose the key and every note in order: up by an augmented fourth (3 letter steps, 6 semitones); then down by a major seventh (6 letter steps, 11 semitones); then up by a major sixth (5 letter steps, 9 semitones).
Use diatonic/chromatic transposition: move letters cyclically through C D E F G A B and adjust accidentals to match the semitone shift. Natural pitch classes are C=0 D=2 E=4 F=5 G=7 A=9 B=11, modulo 12; ignore octaves. Key sharps follow F C G D A E B; flats follow B E A D G C F. In the input, a bare letter uses the source key signature; n, #, b, ##, bb mean absolute offsets 0, +1, -1, +2, -2 from the natural letter, overriding the key for that note only (no carry). Redundant courtesy accidentals change nothing. Retain each shifted letter at every stage: never substitute enharmonic letters.
Return only the final notes in input order, each with an explicit accidental including n for naturals, regardless of the final key. Format example: Gn F# Bbb.

Answer: E# A# Bn Gb F# A# Dn Eb

### Example 2

Prompt:

An arranger has this ascending major-scale fragment in Db major with 5 flats: Gb Ab B C Db Eb Fn Gb.
Transpose the key and every note in order: up by a perfect fourth (3 letter steps, 5 semitones); then down by an augmented fourth (3 letter steps, 6 semitones); then down by a minor second (1 letter step, 1 semitone).
Use diatonic/chromatic transposition: move letters cyclically through C D E F G A B and adjust accidentals to match the semitone shift. Natural pitch classes are C=0 D=2 E=4 F=5 G=7 A=9 B=11, modulo 12; ignore octaves. Key sharps follow F C G D A E B; flats follow B E A D G C F. In the input, a bare letter uses the source key signature; n, #, b, ##, bb mean absolute offsets 0, +1, -1, +2, -2 from the natural letter, overriding the key for that note only (no carry). Redundant courtesy accidentals change nothing. Retain each shifted letter at every stage: never substitute enharmonic letters.
The final key is major on the transposed source tonic (major offsets: 0, 2, 4, 5, 7, 9, 11). Return only its signature as 'N sharps', 'N flats', or 'no sharps or flats'; use the plural even for one. Format example: 3 flats.

Answer: 7 flats
