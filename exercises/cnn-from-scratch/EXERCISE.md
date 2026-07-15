# Build a CNN From Scratch

## The Big Picture

A **convolutional neural network (CNN)** is a kind of neural network that's
specialized for data with spatial structure — images, mostly, but also
spectrograms, video frames, and anything else where "nearby values are
related to each other" is a meaningful statement. The core idea is: instead
of looking at an entire image at once, slide a small pattern-detector across
it, a little patch at a time, and let that same small detector look for its
pattern everywhere in the image. Do that with a few dozen different
detectors, stack a few layers of it, and you get a system that can build up
from "this tiny patch has an edge" to "this tiny patch has a curve" to
"these curves form an eye" to "this image contains a cat."

You've almost certainly benefited from a CNN (or something descended from
one) without knowing it. When your phone's camera app blurs the background
behind a portrait, or draws a box around a face before you take the photo,
or your email provider flags a phishing image, or a photo app lets you
search your camera roll for "dog" — there's a very good chance a
convolution, exactly like the one you're about to build by hand, is
running underneath, sliding a learned filter across pixels. Self-driving
cars use the same mechanism to pick pedestrians and lane markings out of a
camera feed; radiologists use CNN-based tools to flag suspicious regions in
X-rays and MRIs. It's one of the few ideas in machine learning that is both
conceptually simple (a sliding dot product) and directly responsible for a
huge slice of applied AI over the last decade.

Here's the map of what you're about to build, in order. **Stage 1** builds
the atomic operation — a sliding dot product — in 1D, so you can see the
sliding mechanic without also tracking rows and columns. **Stage 2** lifts
that same operation into 2D, which is the shape real images actually come
in. **Stage 3** adds the two knobs every real convolution exposes — stride
(how far the window jumps each step) and padding (a zero border added
before sliding) — because those are exactly the arguments you'll later see
in `keras.layers.Conv2D(strides=..., padding=...)`. **Stage 4** turns a bare
convolution into something that deserves to be called a "layer": a stack of
several filters applied to the same input, each followed by a nonlinearity
(ReLU) so the network can represent more than straight lines. **Stage 5**
adds pooling, which shrinks a feature map down while keeping its strongest
signal. **Stage 6** wires stages 4 and 5 together into an actual
convolution → ReLU → pool pipeline running on a small image you can read by
eye, so you can watch an edge survive the whole trip. **Stage 7** is the
payoff: you run the exact same tiny example through real
`keras.layers.Conv2D` and confirm the numbers match yours.

One thing to be upfront about: this exercise builds the **feature-extraction
backbone** of a CNN — the part that turns raw pixels into a stack of feature
maps — because that's the part that's genuinely new and specific to CNNs.
It deliberately does **not** build two other pieces that a real, trainable
CNN also needs:

- **The classifier head.** After the convolutional backbone produces its
  final feature maps, a real image-classification CNN flattens them into a
  single long vector (`Flatten`), passes that through one or more fully
  connected layers (`Dense`), and ends with a `Softmax` that turns raw
  scores into class probabilities ("73% cat, 12% dog, ..."). That part is
  "ordinary" fully-connected neural network machinery — not specific to
  convolutions — so it's out of scope here.
- **Backpropagation and training.** Everything you build in this exercise is
  a **forward pass**: given fixed filter weights, compute the output. A real
  CNN *learns* those filter weights from data via backpropagation and
  gradient descent — nobody hand-designs the vertical-edge-detector kernel
  you'll use in stage 6; the network discovers something like it on its own
  by seeing thousands of labeled images. Backprop-through-a-convolution is
  offered as an optional stretch goal at the end of this file, but it isn't
  required to call this exercise complete.

Keep both of those in mind as you go: by the end you'll deeply understand
*how a CNN looks at an image*, and you'll know exactly what's missing
between that and *a full, trainable image classifier*.

## What you'll build

You'll implement the forward pass of a convolutional neural network from raw
numpy arrays and nested loops — no deep learning framework — starting with a
1D sliding dot product and ending with a tiny image pipeline (convolution →
ReLU → max pooling) that you'll then reproduce using `keras.layers.Conv2D` to
confirm your numbers match a real library. By the end you'll know exactly
what `filters`, `kernel_size`, `strides`, and `padding` mean, because you'll
have built each one by hand before ever passing it as a keyword argument.

## Learning objectives

- Understand convolution as "slide a small weight matrix over the input and
  take a dot product at every position" — not as a mysterious black box.
- Be able to compute, by hand or in code, how stride and padding change an
  output's shape.
- Understand why a "layer" is a stack of filters plus a nonlinearity (ReLU),
  and why pooling shrinks a feature map while keeping the strongest signal.
- Be able to map every argument of `keras.layers.Conv2D` (or `torch.nn.Conv2d`)
  back to a piece of code you wrote yourself.

## Prerequisites

- Comfortable with Python and basic numpy (array indexing, slicing, `np.sum`).
- No prior deep learning or linear algebra background required beyond
  "a dot product multiplies two same-length vectors elementwise and sums it"
  — and even that gets explained from scratch below, so don't worry if the
  phrase "dot product" is fuzzy right now.
- Install dependencies:

  ```bash
  pip install numpy pytest
  ```

  (Stage 7 is optional and additionally needs `pip install tensorflow` — see
  that stage for details. Nothing else in this exercise depends on it.)

## Time estimate

**1–3 hours** for stages 1–6. Stage 7 (the Keras bridge) adds about 20–30
minutes if you have TensorFlow installed. This sits in the "moderate math"
band — there's no calculus here, just array arithmetic — but stage 4 onward
takes a bit of care to keep shapes straight.

## How to work through this

Each stage below gives you: a plain-language explanation of the sub-concept,
a worked-by-hand trace on small numbers, the exact function or class
signature you need to implement (with type hints and a docstring), 2–3
worked examples showing input → output, and the pytest command to check your
work. Implement each stage in the matching file under `starter/`, then run
its test file. Move to the next stage only once the current one's tests
pass — later stages import from earlier ones, so skipping ahead won't work
anyway.

---

## Stage 1 — Warm-up: 1D convolution

### Concept

A convolution is a **sliding dot product**. Let's unpack both halves of that
phrase, since the rest of this exercise is just this one idea with more
dimensions and more knobs bolted on.

A **dot product** between two same-length lists of numbers means: multiply
the numbers at matching positions, then add up all those products into a
single number. That's it — no matrices, no calculus. `np.dot([a, b, c], [x,
y, z])` computes `a*x + b*y + c*z`. It's the right primitive here because a
convolution, at every position, is asking one question: "how well does this
patch of the signal line up with the pattern I'm looking for?" — and
elementwise-multiply-then-sum is exactly the operation that turns "how well
do these two lists agree, position by position" into a single similarity
score. A large positive dot product means the patch strongly resembles the
kernel; a value near zero means they don't correlate; a large negative value
means the patch looks like the *opposite* of the kernel.

A **kernel** (also called a "filter" — this exercise uses both words for the
same thing) is a short list of numbers representing the pattern you're
looking for. A **sliding window** means: instead of computing that dot
product once, you compute it once per position as the kernel moves
step-by-step across the signal, one slot to the right each time, producing
one output number per position.

Here's that sliding motion drawn out, using the signal `[1, 2, 3, 4, 5]` and
kernel `[1, 0, -1]`:

```
signal:  [ 1   2   3   4   5 ]

position 0:  [1  0 -1]
             [1  2  3]           ->  1*1 + 2*0 + 3*(-1)  = -2

position 1:      [1  0 -1]
                  [2  3  4]      ->  2*1 + 3*0 + 4*(-1)  = -2

position 2:          [1  0 -1]
                      [3  4  5]  ->  3*1 + 4*0 + 5*(-1)  = -2
```

Walking through it by hand: at position 0, the kernel `[1, 0, -1]` lines up
with the first three signal values `[1, 2, 3]`. Multiply elementwise and
sum: `1*1 + 2*0 + 3*(-1) = 1 + 0 - 3 = -2`. Slide the kernel one step to the
right so it now lines up with `[2, 3, 4]`: `2*1 + 3*0 + 4*(-1) = 2 + 0 - 4 =
-2`. Slide once more to line up with `[3, 4, 5]`: `3*1 + 4*0 + 5*(-1) = 3 +
0 - 5 = -2`. The kernel can't slide any further right without running off
the end of the signal, so we stop — three positions, three output values:
`[-2, -2, -2]`.

Notice the kernel `[1, 0, -1]` is doing something specific: it's comparing
"the value on the left" against "the value on the right" of each window
(the middle value gets multiplied by zero, so it's ignored). That's a tiny
1D edge detector — it responds strongly whenever the signal is decreasing
from left to right within the window, which is exactly what happens here
since the signal `[1, 2, 3, 4, 5]` increases steadily by 1 at every step
(so "left minus right" is a constant -2 everywhere). You'll meet this same
"detector" idea again in 2D in stage 6, looking for a vertical edge in an
image instead of a numeric trend in a list.

This is the entire mechanism of a convolution — everything else in this
exercise is this same slide-multiply-sum idea with more dimensions (stage
2), extra knobs for how far and how padded the slide is (stage 3), multiple
kernels applied at once plus a nonlinearity (stage 4), and a second kind of
sliding window that takes a max instead of a dot product (stage 5). We
start in 1D so you can see the sliding-window mechanic clearly before also
juggling rows and columns.

### Signature

```python
def convolve1d(signal: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Slide `kernel` over `signal` and compute the dot product at each position
    (valid convolution: no padding, stride 1).

    Args:
        signal: 1D array, shape (n,)
        kernel: 1D array, shape (k,), k <= n

    Returns:
        1D array, shape (n - k + 1,)

    Example:
        >>> convolve1d(np.array([1, 2, 3, 4, 5]), np.array([1, 0, -1]))
        array([-2., -2., -2.])
    """
    raise NotImplementedError
```

### Worked examples

```python
>>> convolve1d(np.array([1, 2, 3, 4, 5]), np.array([1, 0, -1]))
array([-2., -2., -2.])
# position 0: 1*1 + 2*0 + 3*(-1) = 1 - 3 = -2
# position 1: 2*1 + 3*0 + 4*(-1) = 2 - 4 = -2
# position 2: 3*1 + 4*0 + 5*(-1) = 3 - 5 = -2

>>> convolve1d(np.array([2, 8, -1, 4]), np.array([0.5, 0.5]))
array([5. , 3.5, 1.5])
# a 2-tap averaging kernel: each output is the average of two neighbors

>>> convolve1d(np.array([1.0, 2.0, 3.0]), np.array([1.0, 1.0, 1.0]))
array([6.])
# edge case: kernel is exactly as long as the signal -> a single output value
```

### Run it

```bash
pytest tests/test_01_warmup_conv1d.py -v
```

---

## Stage 2 — 2D convolution

### Concept

Real images aren't lists of numbers, they're grids — rows and columns of
pixel values. So the natural next step is to add a dimension: instead of
sliding a 1D kernel along a 1D signal, slide a small 2D kernel (think of it
as a tiny weighted stencil, a few pixels wide and tall) over a 2D image,
taking a dot product of the whole overlapping patch at each position. "Dot
product of a patch" here means the same elementwise-multiply-then-sum as
before, just applied to a 2D block of numbers instead of a 1D stretch —
multiply every kernel entry by the image value sitting under it, then add
up all of those products into one number.

Picture it as a small transparent stencil sliding over a bigger grid, one
column to the right at a time until it hits the edge, then back to the left
edge and one row down — the same left-to-right, top-to-bottom sweep you'd
use reading a page of text:

```
image (3x3):          kernel (2x2):
+---+---+---+          +---+---+
| 1 | 2 | 3 |          | 1 | 0 |
+---+---+---+          +---+---+
| 4 | 5 | 6 |          | 0 |-1 |
+---+---+---+          +---+---+
| 7 | 8 | 9 |

kernel over top-left patch [[1,2],[4,5]]:
  1*1 + 2*0 + 4*0 + 5*(-1) = 1 - 5 = -4

slide one column right, over [[2,3],[5,6]]:
  2*1 + 3*0 + 5*0 + 6*(-1) = 2 - 6 = -4

slide back to the left edge, one row down, over [[4,5],[7,8]]:
  4*1 + 5*0 + 7*0 + 8*(-1) = 4 - 8 = -4

slide one column right, over [[5,6],[8,9]]:
  5*1 + 6*0 + 8*0 + 9*(-1) = 5 - 9 = -4
```

Four positions fit (the kernel can slide 2 steps across and 2 steps down in
a 3x3 image with a 2x2 kernel), and every one of them lands on `-4` — this
kernel is again a "left column minus right column" detector, and this
particular image increases uniformly enough that the difference comes out
constant. The output is a 2x2 grid of `-4`s, matching the four positions the
kernel fit into.

This is a direct analogy to stage 1 — same sliding-window idea, just over
rows and columns instead of a single axis. Here's your solved stage 1 as a
reminder of the shape, since stage 2 is structurally almost identical, just
with an extra loop for the second dimension:

```python
def convolve1d(signal, kernel):
    n, k = len(signal), len(kernel)
    out = np.zeros(n - k + 1)
    for i in range(n - k + 1):
        out[i] = np.sum(signal[i:i+k] * kernel)
    return out
```

### Signature

```python
def convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Slide `kernel` over `image` and compute the dot product at each position
    (valid convolution, no padding, stride 1).

    Args:
        image: 2D array, shape (H, W)
        kernel: 2D array, shape (kh, kw), kh <= H and kw <= W

    Returns:
        2D array, shape (H - kh + 1, W - kw + 1)

    Example:
        >>> image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> kernel = np.array([[1, 0], [0, -1]])
        >>> convolve2d(image, kernel)
        array([[-4., -4.],
               [-4., -4.]])
    """
    raise NotImplementedError
```

### Worked examples

```python
>>> image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
>>> kernel = np.array([[1, 0], [0, -1]])
>>> convolve2d(image, kernel)
array([[-4., -4.],
       [-4., -4.]])
# top-left 2x2 patch [[1,2],[4,5]]: 1*1 + 2*0 + 4*0 + 5*(-1) = 1 - 5 = -4

>>> image2 = np.ones((4, 4))
>>> kernel2 = np.array([[1, 1], [1, 1]])
>>> convolve2d(image2, kernel2)
array([[4., 4., 4.],
       [4., 4., 4.],
       [4., 4., 4.]])
# every 2x2 patch of ones summed with an all-ones kernel = 4

>>> convolve2d(np.array([[5]]), np.array([[2]]))
array([[10.]])
# edge case: 1x1 image, 1x1 kernel -> a single scalar "convolution"
```

### Run it

```bash
pytest tests/test_02_conv2d.py -v
```

---

## Stage 3 — Stride and padding

### Concept

Real conv layers give you two more knobs, and both of them are just precise
control over the sliding window you already built in stages 1 and 2.

**Stride** is how far the kernel jumps between positions. Every convolution
you've computed so far used stride 1 — the kernel moves one pixel at a time,
visiting every possible position. Stride 2 means "skip every other
position": the kernel jumps two pixels at a time instead of one, so it
visits roughly half as many positions, and the output shrinks accordingly.
Think of it like reading every other word in a sentence instead of every
word — you cover the same span of text but land on fewer stops along the
way, and you get there faster at the cost of resolution.

**Padding** adds a border of zeros around the image *before* convolving.
Without padding, a convolution always shrinks its input a bit (a `kh` x `kw`
kernel eats `kh - 1` rows and `kw - 1` columns off the output, as you saw in
stage 2: a 3x3 image with a 2x2 kernel produced only a 2x2 output). Padding
lets you counteract that shrinkage, and is often chosen so the output comes
out the exact same size as the input — this is usually called "same"
padding in library documentation, as opposed to "valid" padding (no padding
at all, output shrinks), which is what stages 1 and 2 used implicitly.

Here's the shape-arithmetic intuition in one picture. Take a 4x4 image and
zero-pad it by 1 on every side — it becomes a 6x6 grid of mostly zeros with
your original image sitting in the middle:

```
original 4x4:            padded to 6x6 (padding=1):
                          0  0  0  0  0  0
 1  2  3  4               0  1  2  3  4  0
 5  6  7  8       -->      0  5  6  7  8  0
 9 10 11 12                0  9 10 11 12  0
13 14 15 16                0 13 14 15 16  0
                          0  0  0  0  0  0
```

A 2x2 kernel sliding at stride 1 over that padded 6x6 grid now has room to
produce a 5x5 output instead of the 3x3 it would have produced on the
original, unpadded 4x4 image — bigger than the original input, because the
padding added more room to slide than the kernel took away. The general
formula (which you'll implement directly) is:

```
out_h = (H + 2*padding - kh) // stride + 1
out_w = (W + 2*padding - kw) // stride + 1
```

Extend your stage 2 function to accept both `stride` and `padding` as
arguments.

### Signature

```python
def convolve2d_strided(
    image: np.ndarray,
    kernel: np.ndarray,
    stride: int = 1,
    padding: int = 0,
) -> np.ndarray:
    """
    Slide `kernel` over `image` with the given stride and zero-padding.

    Padding is applied symmetrically on all four sides before convolving.
    Stride controls how many pixels the kernel moves between positions.

    Args:
        image: 2D array, shape (H, W)
        kernel: 2D array, shape (kh, kw)
        stride: step size between kernel positions, >= 1
        padding: number of zero-pixels added to each side of the image, >= 0

    Returns:
        2D array, shape:
            out_h = (H + 2*padding - kh) // stride + 1
            out_w = (W + 2*padding - kw) // stride + 1

    Example:
        >>> image = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]])
        >>> kernel = np.array([[1, 0], [0, -1]])
        >>> convolve2d_strided(image, kernel, stride=2, padding=0)
        array([[-5., -5.],
               [-5., -5.]])
    """
    raise NotImplementedError
```

### Worked examples

```python
>>> image = np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]])
>>> kernel = np.array([[1, 0], [0, -1]])

>>> convolve2d_strided(image, kernel, stride=1, padding=0)
array([[-5., -5., -5.],
       [-5., -5., -5.],
       [-5., -5., -5.]])
# same as plain convolve2d: 4x4 in, 2x2 kernel -> 3x3 out

>>> convolve2d_strided(image, kernel, stride=2, padding=0)
array([[-5., -5.],
       [-5., -5.]])
# stride 2 keeps only every other position -> output shrinks to 2x2

>>> convolve2d_strided(image, kernel, stride=1, padding=1)
array([[ -1.,  -2.,  -3.,  -4.,   0.],
       [ -5.,  -5.,  -5.,  -5.,   4.],
       [ -9.,  -5.,  -5.,  -5.,   8.],
       [-13.,  -5.,  -5.,  -5.,  12.],
       [  0.,  13.,  14.,  15.,  16.]])
# padding=1 surrounds the 4x4 image with a border of zeros (6x6), so a 2x2
# kernel at stride 1 now produces a 5x5 output — bigger than the input

# edge case: image smaller than the kernel, only possible with enough padding
>>> convolve2d_strided(np.array([[7]]), np.array([[1,1],[1,1]]), stride=1, padding=1)
array([[7., 7.],
       [7., 7.]])
# a 1x1 image padded by 1 becomes 3x3 of zeros with a 7 in the center;
# each 2x2 window catches exactly one 7 and three zeros
```

### Run it

```bash
pytest tests/test_03_stride_padding.py -v
```

---

## Stage 4 — Multiple filters + ReLU

### Concept

A real conv layer doesn't apply just one kernel — it applies a *stack* of
kernels (called filters) to the same input, each producing its own feature
map, so the layer can learn to detect several different patterns at once
(edges in different directions, corners, textures, color contrasts, and so
on — in a real, trained network, dozens of these per layer). Every filter
slides independently over the same input image using the mechanism you
already built in stages 2–3, and the layer's output stacks all of those
feature maps together. If you have 5 filters, you get 5 feature maps out —
one "answer" per filter, for "how strongly did my pattern show up at every
position."

After convolving, a **nonlinearity** is applied elementwise so the network
can represent more than a straight-line function of its input. Here's the
plain-language reason nonlinearity matters: if you stacked two convolution
layers with nothing but arithmetic in between, the composition of two
linear operations is *still just one linear operation* — you'd gain no
expressive power no matter how many layers you stacked, since a linear
function of a linear function collapses back into a single linear function.
Inserting a simple nonlinear "bend" after each convolution breaks that
collapse, which is what lets a deep stack of layers represent genuinely
complex functions (curved decision boundaries, "this is a cat" from raw
pixels) rather than only straight lines and planes.

The standard nonlinearity used after a conv layer is **ReLU** (rectified
linear unit): `max(0, x)`. It's about as simple as a nonlinear function can
be — for any negative input it outputs exactly zero, and for any
non-negative input it just passes the value through unchanged. Trace it by
hand on `[-2, -1, 0, 1, 2]`: the first two entries are negative, so they
become `0`; the `0` stays `0` (it's not negative, so it passes through
unchanged); `1` and `2` are already non-negative, so they pass through
unchanged too. Result: `[0, 0, 0, 1, 2]`.

Applied after a convolution, ReLU has an intuitive effect: a filter's raw
output is a similarity score that can be positive (patch looks like the
pattern), negative (patch looks like the *opposite* of the pattern), or
near zero (patch is unrelated to the pattern). ReLU keeps the positive
"yes, this pattern is here" signal and zeroes out the negative
"anti-pattern" signal, on the idea that "how strongly is the opposite
pattern present" usually isn't useful information to pass forward. You'll
see this concretely in the worked example below: one filter's raw output is
uniformly negative and gets wiped out entirely by ReLU; another filter's
raw output is uniformly positive and passes through completely unchanged.

This is the first stage that feels like "a layer" rather than a bare
function — you're building both the elementwise ReLU and a small
`ConvLayer` class that owns a stack of kernels and knows how to run all of
them, plus ReLU, over an input in one call.

### Signature

```python
def relu(x: np.ndarray) -> np.ndarray:
    """
    Elementwise rectified linear unit: max(0, x).

    Example:
        >>> relu(np.array([-2, -1, 0, 1, 2]))
        array([0, 0, 0, 1, 2])
    """
    raise NotImplementedError


class ConvLayer:
    """
    A convolutional layer: a stack of kernels (filters) applied to the same
    input, each followed by ReLU.

    Args:
        kernels: 3D array, shape (num_filters, kh, kw) — one kernel per filter
        stride: shared stride for every filter
        padding: shared zero-padding for every filter
    """

    def __init__(self, kernels: np.ndarray, stride: int = 1, padding: int = 0):
        raise NotImplementedError

    def forward(self, image: np.ndarray) -> np.ndarray:
        """
        Apply every filter to `image`, then ReLU each result.

        Args:
            image: 2D array, shape (H, W)

        Returns:
            3D array, shape (num_filters, out_h, out_w) — one feature map
            per filter, using the same out_h/out_w formula as
            convolve2d_strided.

        Example:
            >>> image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
            >>> k1 = np.array([[1, 0], [0, -1]])
            >>> k2 = np.array([[-1, 0], [0, 1]])
            >>> layer = ConvLayer(np.stack([k1, k2]), stride=1, padding=0)
            >>> layer.forward(image)
            array([[[0., 0.],
                    [0., 0.]],
            <BLANKLINE>
                   [[4., 4.],
                    [4., 4.]]])
        """
        raise NotImplementedError
```

### Worked examples

```python
>>> relu(np.array([-2, -1, 0, 1, 2]))
array([0, 0, 0, 1, 2])

>>> image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
>>> k1 = np.array([[1, 0], [0, -1]])   # this kernel's raw output is -4 everywhere
>>> k2 = np.array([[-1, 0], [0, 1]])   # this kernel's raw output is +4 everywhere
>>> layer = ConvLayer(np.stack([k1, k2]), stride=1, padding=0)
>>> layer.forward(image)
array([[[0., 0.],
        [0., 0.]],
<BLANKLINE>
       [[4., 4.],
        [4., 4.]]])
# filter 1's raw convolution is all -4 -> ReLU kills it entirely (all zero)
# filter 2's raw convolution is all +4 -> ReLU passes it through unchanged
# this is exactly why ReLU matters: some filters "fire," others go silent

>>> layer2 = ConvLayer(np.stack([np.array([[1, 1], [1, 1]])]), stride=2, padding=1)
>>> layer2.forward(np.zeros((2, 2))).shape
(1, 2, 2)
# edge case: an all-zero image still produces a well-shaped (but all-zero)
# output — ReLU(0) == 0, so nothing breaks with a degenerate input
```

### Run it

```bash
pytest tests/test_04_conv_layer.py -v
```

---

## Stage 5 — Pooling

### Concept

Pooling shrinks a feature map by summarizing small neighborhoods down to a
single number. It solves two practical problems at once: it reduces how
much computation later layers need to do (a smaller feature map is cheaper
to process), and it adds a bit of *translation tolerance* — a feature
detected slightly off-position in the input still gets picked up in the
pooled output, because pooling only cares about the strongest response in a
neighborhood, not its exact pixel location.

**Max pooling** — take the maximum value in each window — is the standard
choice, and it's the same sliding-window idea you've now built three times
(convolution in 1D, convolution in 2D, and now this), just with "take the
max" in place of "compute the dot product." It preserves "was this pattern
present anywhere in this region," which is usually what you want right
after a filter has just told you, pixel by pixel, where an edge or texture
showed up — you often don't need to know the edge's *exact* pixel, just that
it's somewhere in this neighborhood.

Trace it by hand on a small feature map:

```
feature map (4x4):
+---+---+---+---+
| 1 | 3 | 2 | 4 |
+---+---+---+---+
| 5 | 6 | 1 | 2 |
+---+---+---+---+
| 1 | 2 | 9 | 8 |
+---+---+---+---+
| 3 | 4 | 7 | 6 |
+---+---+---+---+

2x2 windows, stride 2 (non-overlapping, tiled like a checkerboard):

top-left window     [[1,3],       max(1,3,5,6)  = 6
                      [5,6]]
top-right window    [[2,4],       max(2,4,1,2)  = 4
                      [1,2]]
bottom-left window  [[1,2],       max(1,2,3,4)  = 4
                      [3,4]]
bottom-right window [[9,8],       max(9,8,7,6)  = 9
                      [7,6]]
```

Each window's four numbers collapse down to their single largest value, and
the four windows (arranged 2x2, since the windows themselves tile a 4x4 map
with 2x2, non-overlapping windows) become a 2x2 output: `[[6, 4], [4, 9]]`.
Notice that unlike convolution, there's no kernel of *weights* here — no
multiplying, no learned parameters — pooling is a fixed, parameter-free
operation that just reports "what's the biggest value in this
neighborhood."

This stage is short and should feel like a fast confidence-builder after
stage 4 — it reuses the sliding-window shape you already know, with a
simpler operation inside the window.

### Signature

```python
def max_pool2d(feature_map: np.ndarray, size: int, stride: int) -> np.ndarray:
    """
    Slide a `size` x `size` window over `feature_map` and take the max in
    each window.

    Args:
        feature_map: 2D array, shape (H, W)
        size: window side length, >= 1
        stride: step size between windows, >= 1

    Returns:
        2D array, shape:
            out_h = (H - size) // stride + 1
            out_w = (W - size) // stride + 1

    Example:
        >>> fm = np.array([[1, 3, 2, 4], [5, 6, 1, 2], [1, 2, 9, 8], [3, 4, 7, 6]])
        >>> max_pool2d(fm, size=2, stride=2)
        array([[6., 4.],
               [4., 9.]])
    """
    raise NotImplementedError
```

### Worked examples

```python
>>> fm = np.array([[1, 3, 2, 4], [5, 6, 1, 2], [1, 2, 9, 8], [3, 4, 7, 6]])

>>> max_pool2d(fm, size=2, stride=2)
array([[6., 4.],
       [4., 9.]])
# non-overlapping 2x2 windows: top-left window [[1,3],[5,6]] -> max is 6

>>> max_pool2d(fm, size=2, stride=1)
array([[6., 6., 4.],
       [6., 9., 9.],
       [4., 9., 9.]])
# overlapping windows (stride < size) -> a bigger, overlapping output

>>> max_pool2d(np.array([[3, 1], [2, 5]]), size=2, stride=2)
array([[5.]])
# edge case: window size equals the whole map -> a single output value
```

### Run it

```bash
pytest tests/test_05_pooling.py -v
```

---

## Stage 6 — Integration

### Concept

Now wire everything together and watch it actually work on an image you can
read by eye. This stage doesn't introduce a new mechanism — it's entirely
composed of pieces you've already built and tested (`ConvLayer` from stage
4, `max_pool2d` from stage 5) — but seeing them chained into one pipeline on
a real, if tiny, image is a different and more convincing experience than
passing unit tests on each piece in isolation.

Take a small 6x6 image with an obvious vertical edge (left half low values,
right half high values — imagine it as a miniature photo of a dark wall
next to a bright window). Run it through your `ConvLayer` with a
vertical-edge-detecting kernel `[[-1, 1], [-1, 1]]` — notice the shape: this
kernel subtracts the left column of every 2x2 window from the right column,
so it produces a large value exactly where pixel intensity jumps from low
to high moving left to right, and near zero where the image is flat. Then
run the result through `max_pool2d`. You should see the edge survive the
whole pipeline: the convolution should light up right where the edge is,
and pooling should shrink the map while keeping that signal visible rather
than averaging it away.

This is the moment your unit-tested functions become a system that does
something you can point at: "here is the input image, here is the edge my
kernel found, here is the shrunk-down feature map that still shows exactly
where that edge was."

### Signature

```python
def build_edge_image() -> np.ndarray:
    """
    A 6x6 image with a vertical edge: the left half is 0, the right half is 1.

    Returns:
        2D array, shape (6, 6):
        array([[0., 0., 0., 1., 1., 1.],
               [0., 0., 0., 1., 1., 1.],
               [0., 0., 0., 1., 1., 1.],
               [0., 0., 0., 1., 1., 1.],
               [0., 0., 0., 1., 1., 1.],
               [0., 0., 0., 1., 1., 1.]])
    """
    raise NotImplementedError


def run_pipeline(
    image: np.ndarray,
    kernels: np.ndarray,
    pool_size: int,
    pool_stride: int,
) -> np.ndarray:
    """
    Run `image` through a ConvLayer (stride=1, padding=0) built from `kernels`,
    then max-pool every resulting feature map.

    Args:
        image: 2D array, shape (H, W)
        kernels: 3D array, shape (num_filters, kh, kw)
        pool_size: pooling window size
        pool_stride: pooling stride

    Returns:
        3D array, shape (num_filters, pooled_h, pooled_w)

    Example:
        >>> image = build_edge_image()
        >>> kernel = np.array([[-1, 1], [-1, 1]])
        >>> run_pipeline(image, np.stack([kernel]), pool_size=2, pool_stride=2)
        array([[[0., 2.],
                [0., 2.]]])
    """
    raise NotImplementedError
```

### Worked examples

```python
>>> image = build_edge_image()
>>> image.shape
(6, 6)

>>> vertical_edge_kernel = np.array([[-1, 1], [-1, 1]])
>>> run_pipeline(image, np.stack([vertical_edge_kernel]), pool_size=2, pool_stride=2)
array([[[0., 2.],
        [0., 2.]]])
# the raw conv+ReLU output is a 5x5 map that's 0 everywhere except a bright
# column of 2s right where the edge is (column index 2, between the 0s and
# 1s of the input) — pooling then shrinks that 5x5 map to 2x2 while keeping
# the bright column visible in the right-hand column of the pooled output

>>> run_pipeline(np.zeros((6, 6)), np.stack([vertical_edge_kernel]), pool_size=2, pool_stride=2).sum()
0.0
# edge case: a flat, featureless image produces an all-zero pipeline output
# end to end — nothing to detect, nothing fires
```

### Run it

```bash
pytest tests/test_06_integration.py -v
```

---

## Stage 7 — Bridge to Keras

### Concept

Before writing any code in this stage, it's worth pausing on what **Keras**
actually is, since it's easy to let a library name do unexplained work.
Keras is a high-level API — a set of building blocks like `Dense`,
`Conv2D`, and `MaxPooling2D` that you snap together into a network — sitting
on top of a lower-level numerical engine, typically **TensorFlow**. Keras
itself doesn't do the heavy numerical lifting; it constructs a description
of the network's layers and hands the actual array math (convolutions,
matrix multiplies, gradient computation during training) down to
TensorFlow, which runs it efficiently — often on a GPU, using highly
optimized, vectorized code instead of the plain Python `for` loops you just
wrote by hand. In other words: `keras.layers.Conv2D` is not a different
*idea* from your `ConvLayer` — it's the same slide-multiply-sum operation
you built in stages 2–4, implemented in fast, production-grade code and
wrapped in a convenient, reusable object.

Everything you built in stages 2–6 is, mechanically, what
`keras.layers.Conv2D` does — just written by hand, over one image, with one
channel, using plain Python loops instead of a fast vectorized/GPU
implementation. In this stage you run the *same* stage-6 edge image and
kernel through a real `keras.layers.Conv2D` layer, manually setting its
weights to match your kernel, and confirm the outputs agree (up to floating
point rounding). Concretely: Keras's `Conv2D` computes cross-correlation (no
kernel flip) — exactly what you implemented — so with matching weights and
zero bias, your numbers and Keras's numbers should match exactly.

This is also a good moment to connect Keras's keyword arguments back to the
knobs you built by hand: `filters` is "how many kernels" (stage 4),
`kernel_size` is your kernel's shape (stages 1–2), and `strides=` /
`padding=` are exactly the stride and padding you implemented in stage 3.
There's nothing left in a `Conv2D` call that you haven't already built and
named yourself.

This stage is **optional** and needs an extra dependency:

```bash
pip install tensorflow
```

None of the other stages or the main test suite depend on TensorFlow being
installed — if you don't have it, skip this stage, the rest of the exercise
stands on its own.

### Signature

```python
def conv2d_with_keras(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Run `image` through a single-filter keras.layers.Conv2D layer whose
    weights are manually set to `kernel`, with valid padding and stride 1,
    and return the resulting feature map with the same (out_h, out_w) shape
    your own convolve2d would produce.

    Args:
        image: 2D array, shape (H, W)
        kernel: 2D array, shape (kh, kw)

    Returns:
        2D array, shape (H - kh + 1, W - kw + 1) — the Conv2D output for the
        single filter, with the batch and channel dimensions squeezed out.

    Notes:
        - keras.layers.Conv2D expects input shape (batch, H, W, channels)
          and weights shape (kh, kw, in_channels, out_channels). Reshape
          `image` to (1, H, W, 1) and `kernel` to (kh, kw, 1, 1) accordingly.
        - Set the layer's bias to 0 so the comparison is exact.
        - Build the layer with padding="valid", strides=(1, 1), so its
          output shape matches convolve2d's formula exactly.

    Example:
        >>> image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype="float32")
        >>> kernel = np.array([[1, 0], [0, -1]], dtype="float32")
        >>> conv2d_with_keras(image, kernel)
        array([[-4., -4.],
               [-4., -4.]], dtype=float32)
    """
    raise NotImplementedError
```

### Worked examples

```python
>>> image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype="float32")
>>> kernel = np.array([[1, 0], [0, -1]], dtype="float32")
>>> conv2d_with_keras(image, kernel)
array([[-4., -4.],
       [-4., -4.]], dtype=float32)
# identical numbers to stage 2's convolve2d(image, kernel) worked example --
# this is the payoff: `filters=1` is "how many kernels," `kernel_size=(2,2)`
# is your kernel's shape, `strides=` and `padding=` are exactly the knobs
# you built in stage 3

>>> edge_image = build_edge_image().astype("float32")  # from stage 6
>>> vertical_edge_kernel = np.array([[-1, 1], [-1, 1]], dtype="float32")
>>> conv2d_with_keras(edge_image, vertical_edge_kernel)
# matches your stage 6 pre-ReLU, pre-pooling conv output: all zeros except
# a bright column of 2.0 right where the edge is
```

### Run it

```bash
pytest tests/test_07_bridge_to_keras.py -v
```

If TensorFlow isn't installed, this test is automatically skipped rather than
failing — you'll see an `s` in the pytest output instead of a `.` or `F`.

---

## Stretch (optional, not built out here)

If you want to go deeper: implement the **backward pass** for stage 2's
`convolve2d` — i.e., given the gradient of some loss with respect to the
convolution's output, compute the gradient with respect to the kernel (and
optionally with respect to the input image). This is the other half of what
a real deep learning framework does automatically via autodiff, and working
it out by hand for a plain convolution is the single best way to understand
what "backprop through a conv layer" actually means. A reasonable follow-up
beyond that: extend it to a strided transpose convolution (the operation
used to *upsample* feature maps, e.g. in image segmentation or generative
models). Neither is required to consider this exercise complete.

---

## Bringing It All Together

Step back and look at what you've actually built. Starting from a bare
sliding dot product on a list of five numbers, you now have: a 2D
convolution with configurable stride and padding, a `ConvLayer` that stacks
several filters and applies ReLU to each, a `max_pool2d` that shrinks a
feature map while keeping its strongest signal, and a `run_pipeline`
function that chains a conv layer and pooling into one system — and you
watched that system detect a real edge in a 6x6 image and survive the whole
trip to a 2x2 output. Then you confirmed, number for number, that a real
`keras.layers.Conv2D` layer does exactly the same arithmetic your
`ConvLayer` does, just implemented faster and more generally.

That's the feature-extraction backbone of a CNN — the part that turns raw
pixels into increasingly abstract feature maps. Stack several rounds of
`ConvLayer` → `max_pool2d` on top of each other (which is exactly what
`run_pipeline` does once, but real networks do it repeatedly), and the
feature maps get smaller in width/height but richer in what each position
"means": early layers' filters tend to respond to edges and simple textures
much like your `[[-1, 1], [-1, 1]]` kernel did, middle layers combine those
into corners and simple shapes, and deep layers respond to complex,
recognizable parts of objects.

Remember the two pieces named in the Big Picture section at the top that
this exercise deliberately didn't build. First, the **classifier head**:
after the last pooling stage, a real network flattens the final stack of
feature maps into one long vector (`Flatten`), passes it through one or more
`Dense` (fully-connected) layers, and finishes with a `Softmax` that turns
raw scores into class probabilities. Your `ConvLayer` and `max_pool2d`
would plug directly into such a network as its first few layers — everything
after the last pooling step is "ordinary" fully-connected network machinery,
not something specific to convolutions. Second, **backpropagation and
training**: every kernel you used in this exercise — the edge detectors, the
averaging filter — was handed to you fully-formed. A real CNN starts with
random kernel values and *learns* good ones from thousands or millions of
labeled examples via backpropagation and gradient descent, which is why the
stretch goal above (deriving the backward pass of a convolution by hand) is
the natural next step if you want to see where those kernel values actually
come from.

With that mental model in place, the everyday systems mentioned back in the
Big Picture stop being magic: an image classifier tagging photos by content,
a medical imaging tool flagging a suspicious region on a scan, a
self-driving car's perception stack picking out lane lines and pedestrians
from a camera feed, a phone unlocking via face detection — all of them run
a feature-extraction backbone built from the exact same sliding
dot-product-then-nonlinearity-then-pooling pattern you just implemented by
hand, just deeper, wider, and trained on far more data than a 6x6 toy image.

---

## Run everything

Once all stages are implemented, run the whole suite from inside this
exercise folder:

```bash
pytest tests/ -v
```

---

Want to do this interactively instead, with hints and a review of your
finished code? Install the learn-by-building skill:
https://github.com/<your-username>/<your-learn-by-building-repo>
