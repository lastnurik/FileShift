# Limit v1 images to PNG, JPEG, and WebP still images

V1 supports conversion between PNG, JPEG, and WebP for still images. Animated images, HEIC, SVG, TIFF, and camera RAW are deferred to keep the initial codec and fidelity test scope bounded.

When an input contains transparency, converting to JPEG composites it onto white and the popup labels the choice “JPEG — white background” before conversion. PNG and WebP outputs preserve transparency.

PNG and WebP use lossless encoding. JPEG uses a fixed high-quality setting validated with fixtures once the codec is selected. Quality sliders and file-size presets are deferred. Metadata handling and resource limits remain to be resolved during implementation. Codec availability and route correctness must be verified before a route is advertised.
