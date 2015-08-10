#Available memory Plugin
This is a very simple plugin that provides an accurate available memory metric based on the `free` command. It solves the problem of the default memory metrics not accounting for buffers/cached memory, which can cause low memory alerts on servers that are holding a large cache.
