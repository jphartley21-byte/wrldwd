"""ww: the Worldwide writer. The approved plan is kept in Joe's Claude plans folder (the-purpose-of-this-smooth-candle.md).

Control plane only (Python 3.13). Never imports torch; audio and embedding work runs elsewhere.
The deterministic primitives live in toolkit/ and are reached ONLY through ww.bridge.
"""
__version__ = "0.1.0"
