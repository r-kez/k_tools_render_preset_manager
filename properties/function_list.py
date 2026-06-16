import bpy

## ("", ""),
## ("Property", "Display Name") - Regular properties - No need for 'bpy.scene'
## ("<ACTIVE_VIEW_LAYER>.use_pass_combined", "Pass: Combined"), - For properties that have the view layer name on it
## BV = Blender Version

## Curves needs a special treatment
CURVE_MAPPING_PATHS = [
    "render.motion_blur_shutter_curve",
    "view_settings.curve_mapping",
    "render.image_settings.view_settings.curve_mapping",
    ]

COMMON_COLOR_MANAGEMENT = [
        ("display_settings.display_device",             "Color Management: Display Device"),
        ("view_settings.view_transform",                "Color Management: View Transform"),
        ("view_settings.look",                          "Color Management: Look"),
        ("view_settings.exposure",                      "Color Management: Exposure"),
        ("view_settings.gamma",                         "Color Management: Gamma"),
        # Curves
        ("view_settings.use_curve_mapping",             "Color Management: Use Curve Mapping"),
        # WHite Balance
        ("view_settings.use_white_balance",             "Color Management: Use White Balance"),
        ("view_settings.white_balance_temperature",     "Color Management: White Temperature"),
        ("view_settings.white_balance_tint",            "Color Management: White Tint"),
        # Working Space
        ("bpy.data.colorspace.working_space",           "Color Management: Working Color Space"),   
        ("sequencer_colorspace_settings.name",          "Color Management: Sequencer Colorspace"),
        # Advanced
        ("display_settings.emulation",                  "Color Management: Display Emulation"),
    ]

OCTANE_OUTPUT_PROPS = [
    # Output for Octane Render
        ("octane.use_octane_export",                         "Octane Output: Enable Octane Output"),         # Octane
        ("octane.reuse_blender_output_path",                 "Octane Output: Reuse Blender's Output Path"),  # Octane
        ("octane.octane_output_path",                        "Octane Output: Specific Output Path"),         # Octane
        ("octane.octane_export_prefix_tag",                  "Octane Output: Prefix Tag"),   # Octane
        ("octane.octane_export_postfix_tag",                 "Octane Output: Postfix Tag"),  # Octane
        ("octane.octane_export_mode",                        "Octane Output: Export Mode"),  # Octane
        ("octane.octane_export_file_type",                   "Octane Output: File Type"),    # Octane
        ("octane.octane_integer_bit_depth",                  "Octane Output: Bit Depth"),    # Octane
        ("octane.gui_octane_export_ocio_color_space_name",   "Octane Output: Color Space"),  # Octane
    ]

RENDER_SETTINGS = {
    "RENDER_ENGINE": [
    # Scene:   
        # Render Engine
        ("render.engine", "Render Engine: Render Engine"),
    ],
    "CYCLES": [
# =============================================================================
# CYCLES ENGINE
# =============================================================================
    # Scene    
        #("cycles.feature_set",                    "Cycles: Feature Set"), # [REMOVED] Obsolete
        ("cycles.device",                           "Cycles: Device"),
        ("cycles.shading_system",                   "Cycles: Open Shading Language"),   
    # Sampling:
        # Viewport Sampling
        ("cycles.use_preview_adaptive_sampling",    "Viewport: Adaptative Sampling"),
        ("cycles.preview_adaptive_threshold",       "Viewport: Noise Threshold"),
        ("cycles.preview_samples",                  "Viewport: Samples"),
        ("cycles.preview_adaptive_min_samples",     "Viewport: Min Samples"),
        # Viewport Preview Denoising:
        ("cycles.use_preview_denoising",            "Viewport: Denoise"),
        ("cycles.preview_denoiser",                 "Viewport: Denoiser"),
        ("cycles.preview_denoising_input_passes",   "Viewport: Denoise Passes"),
        ("cycles.preview_denoising_prefilter",      "Viewport: Prefilter"),
        ("cycles.preview_denoising_quality",        "Viewport: Denoise Quality"),
        ("cycles.preview_denoising_start_sample",   "Viewport: Start Sample"),
        ("cycles.preview_denoising_use_gpu",        "Viewport: Denoise Use GPU"),
        # Render Sampling
        ("cycles.use_adaptive_sampling",            "Render: Adaptative Sampling"),
        ("cycles.adaptive_threshold",               "Render: Noise Threshold"),
        ("cycles.samples",                          "Render: Samples"),
        ("cycles.adaptive_min_samples",             "Render: Min Samples"),
        ("cycles.time_limit",                       "Render: Time Limit"),
        ("cycles.use_denoising",                    "Render: Denoise"),
        # Render Denoising   :
        ("cycles.denoiser",                     "Render: Denoiser"),
        ("cycles.denoising_input_passes",       "Render: Denoise Passes"),
        ("cycles.denoising_prefilter",          "Render: Denoising Prefilter"),
        ("cycles.denoising_quality",            "Render: Denoising Quality"),
        ("cycles.denoising_use_gpu",            "Render: Denoise Use GPU"),
        # Path Guiding - CPU Only
        ("cycles.use_guiding",                      "Path Guiding"),
        ("cycles.guiding_training_samples",         "Path Guiding: Training Samples"),
        ("cycles.use_surface_guiding",              "Path Guiding: Surface Guiding"),
        ("cycles.use_volume_guiding",               "Path Guiding: Volume Guiding"),
        ("cycles.guiding_directional_sampling_type", "Path Guiding: Directional Sampling"), # [ADDED]
        ("cycles.guiding_distribution_type",        "Path Guiding: Distribution Type"), # [ADDED]
        ("cycles.guiding_roughness_threshold",      "Path Guiding: Roughness Threshold"), # [ADDED]
        ("cycles.surface_guiding_probability",      "Path Guiding: Surface Probability"), # [ADDED]
        ("cycles.use_deterministic_guiding",        "Path Guiding: Use Deterministic"), # [ADDED]
        ("cycles.use_guiding_direct_light",         "Path Guiding: Guide Direct Light"), # [ADDED]
        ("cycles.use_guiding_mis_weights",          "Path Guiding: MIS Weights"), # [ADDED]
        ("cycles.volume_guiding_probability",       "Path Guiding: Volume Probability"), # [ADDED]
        # Lights:
        ("cycles.use_light_tree",               "Lights: Use Light Tree"),
        ("cycles.light_sampling_threshold",     "Lights: Light Sampling Threshold"),
        # Advanced:
        ("cycles.sampling_pattern",             "Lights: Sampling Pattern"),
        ("cycles.seed",                         "Lights: Seed"),
        ("cycles.use_animated_seed",            "Lights: Use Animated Seed"),
        ("cycles.auto_scrambling_distance",     "Lights: Auto Scrambling Distance"),
        ("cycles.preview_scrambling_distance",  "Lights: Viewport Scrambling Distance"),
        ("cycles.scrambling_distance",          "Lights: Render Scrambling Distance"),
        ("cycles.min_light_bounces",            "Lights: Min Light Bounces"),
        ("cycles.min_transparent_bounces",      "Lights: Min Transparent Bounces"),
        ("cycles.use_sample_subset",            "Lights: Use Sample Subset"),
        ("cycles.use_layer_samples",            "Lights: Use Per-View Layer Samples"),
        ("world.cycles.is_caustics_light",      "Advanced: Is Caustics Light"), # [ADDED]
        ("world.cycles.sample_map_resolution",  "Advanced: Sample Map Resolution"), # [ADDED]
        ("world.cycles.sampling_method",        "Advanced: Sampling Method"), # [ADDED]
        # Sample Subset
        ("cycles.sample_offset",            "Sample Subset: Sample Offset"),
        ("cycles.sample_subset_length",     "Sample Subset: Length"),
    # Light Paths:
        # Max Bounces
        ("cycles.max_bounces",              "Light Paths: Max Bounces Total"),
        ("cycles.diffuse_bounces",          "Light Paths: Diffuse Bounces"),
        ("cycles.glossy_bounces",           "Light Paths: Glossy Bounces"),
        ("cycles.transmission_bounces",     "Light Paths: Transmission Bounces"),
        ("cycles.volume_bounces",           "Light Paths: Volume Bounces"),
        ("cycles.transparent_max_bounces",  "Light Paths: Transparent Bounces"),
        # ClampingLight Paths: 
        ("cycles.sample_clamp_direct",      "Light Paths: Clamp Direct"),
        ("cycles.sample_clamp_indirect",    "Light Paths: Clamp Indirect"),
        # Caustics  Light Paths: 
        ("cycles.blur_glossy",              "Light Paths: Filter Glossy"),
        ("cycles.caustics_reflective",      "Light Paths: Reflective Caustics"),
        ("cycles.caustics_refractive",      "Light Paths: Refractive Caustics"),
    # Fast GI Approximation:
        ("cycles.use_fast_gi",              "Fast GI: Use Fast GI"),
        ("cycles.fast_gi_method",           "Fast GI: Method"),
        ("world.light_settings.ao_factor",  "Fast GI: AO Factor"),
        ("world.light_settings.distance",   "Fast GI: AO Distance"),
        ("cycles.ao_bounces",               "Fast GI: AO Bounces Viewport"),
        ("cycles.ao_bounces_render",        "Fast GI: AO Bounces Render"),
    # Volume:
        ("cycles.volume_step_rate",         "Volume: Step Rate"),
        ("cycles.volume_preview_step_rate", "Volume: Viewport Step Rate"),
        ("cycles.volume_max_steps",         "Volume: Max Steps"),
        ("cycles.volume_biased",            "Volume: Biased"),
        ("world.cycles.volume_interpolation", "Volume: Interpolation"), # [ADDED]
        ("world.cycles.volume_sampling",    "Volume: Sampling"), # [ADDED]
        ("world.cycles.volume_step_size",   "Volume: Step Size"), # [ADDED]
    # Curves:
        ("cycles_curves.shape",             "Curves: Shape"),
        ("cycles_curves.subdivisions",      "Curves: Subdivisions"),
        ("render.hair_type",                "Curves: Hair Type"),
        ("render.hair_subdiv",              "Curves: Hair Subdivisions"),
    # Subdivision:
        ("cycles.dicing_rate",              "Subdivision: Dicing Rate Render"),
        ("cycles.preview_dicing_rate",      "Subdivision: Dicing Rate Viewport"),
        ("cycles.offscreen_dicing_scale",   "Subdivision: Offscreen Scale"),
        ("cycles.max_subdivisions",         "Subdivision: Max Subdivisions"),
        ("cycles.dicing_camera",            "Subdivision: Dicing Camera"),
    # Simplify:
        # Simplify Viewport
        ("render.use_simplify",                         "Simplify: Use Simplify"),
        ("render.simplify_subdivision",                 "Simplify: Viewport Max Subdivision"),
        ("render.simplify_child_particles",             "Simplify: Viewport Child Particles"),
        ("cycles.texture_limit",                        "Simplify: Viewport Texture Limit"),
        ("render.simplify_volumes",                     "Simplify: Viewport Volumes"),
        ("render.use_simplify_normals",                 "Simplify: Viewport Normals"),
        # Simplify Render
        ("render.simplify_subdivision_render",          "Simplify: Render Max Subdivision"),
        ("render.simplify_child_particles_render",      "Simplify: Render Child Particles"),
        ("cycles.texture_limit_render",                 "Simplify: Render Texture Limit"),
        # Culling       
        ("cycles.use_camera_cull",                      "Simplify: Use Camera Cull"),
        ("cycles.camera_cull_margin",                   "Simplify: Camera Cull Margin"),
        ("cycles.use_distance_cull",                    "Simplify: Use Distance Cull"),
        ("cycles.distance_cull_margin",                 "Simplify: Distance Cull Margin"),
        # Grease Pencil
        ("render.simplify_gpencil",                     "Simplify: Simplify Grease Pencil"),
        ("render.simplify_gpencil_onplay",              "Simplify: Grease Pencil On Play"),
        ("render.simplify_gpencil_view_fill",           "Simplify: Grease Pencil Fill"),
        ("render.simplify_gpencil_modifier",            "Simplify: Grease Pencil Modifiers"),
        ("render.simplify_gpencil_shader_fx",           "Simplify: Grease Pencil Shader FX"),
        ("render.simplify_gpencil_tint",                "Simplify: Grease Pencil Tint"),
        ("render.simplify_gpencil_antialiasing",        "Simplify: Grease Pencil Anti-Aliasing"),
    # Motion Blur:
        ("render.use_motion_blur",                      "Motion Blur: Use Motion Blur"),
        ("render.motion_blur_position",                 "Motion Blur: Position"),
        ("render.motion_blur_shutter",                  "Motion Blur: Shutter"),
        ("cycles.rolling_shutter_type",                 "Motion Blur: Rolling Shutter"),
        ("cycles.rolling_shutter_duration",             "Motion Blur: Shutter Duration"),
        ("render.motion_blur_shutter_curve",            "Motion Blur: Shutter Curve"),
    # Film
        ("cycles.film_exposure",                        "Film: Exposure"),
        ("cycles.film_transparent_glass",               "Film: Transparent Glass"),
        # Pixel Filter      
        ("cycles.pixel_filter_type",                    "Film: Pixel Filter"),
        ("cycles.filter_width",                         "Film: Filter Width"),
        ("render.film_transparent",                     "Film: Transparent"),
        ("cycles.film_transparent_roughness",           "Film: Transparent Roughness"),
    # Performance:
        # Compositor
        ("render.compositor_device",                    "Performance: Compositor Device"),
        ("render.compositor_precision",                 "Performance: Compositor Precision"),
        # Denoise Nodes
        ("render.compositor_denoise_final_quality",     "Performance: Denoise Quality"),
        # Threads
        ("render.threads_mode",                         "Performance: Threads Mode"),
        ("render.threads",                              "Performance: Threads"),
        # Memory            
        ("cycles.use_auto_tile",                        "Performance: Use Auto Tile"),
        ("cycles.tile_size",                            "Performance: Tile Size"),
        # Texture Cache
        ("render.use_texture_cache",                    "Performance: Use Texture Cache"),  # BV: 5.2
        ("render.use_auto_generate_texture_cache",      "Performance: Use Auto Generate Texture Cache"), # BV: 5.2
        # Acceleration Structure            
        ("cycles.debug_use_spatial_splits",             "Performance: Use Spatial Splits"),   # CPU ONLY
        ("cycles.debug_use_compact_bvh",                "Performance: Use Compact BVH"),      # CPU ONLY
        ("cycles.debug_bvh_time_steps",                 "Performance: BVH Time Steps"),
        ("cycles.debug_use_hair_bvh",                   "Performance: Use Hair BVH"),
        # Final Render          
        ("render.use_persistent_data",                  "Performance: Persistent Data"),
        # Viewport          
        ("render.preview_pixel_size",                   "Performance: Pixel Size"),
    # Grease Pencil  
        ("grease_pencil_settings.antialias_threshold",  "Grease Pencil: Anti-Alias Threshold"),
    # Freestyle:
        ("render.use_freestyle",                        "Freestyle: Use Freestyle"),
        ("render.line_thickness_mode",                  "Freestyle: Thickness Mode"),
        ("render.line_thickness",                       "Freestyle: Line Thickness"),
    # Color Management: 
    # Come from the unified lsit

    # Debug:
        ("cycles.debug_use_cpu_sse42",              "Debug: Use CPU SSE4.2"),
        ("cycles.debug_use_cpu_avx2",               "Debug: Use CPU AVX2"),
        ("cycles.debug_bvh_layout",                 "Debug: BVH Layout"),
        ("cycles.debug_use_metal_adaptive_compile", "Debug: Metal Adaptive Compile"),
        ("cycles.debug_use_cuda_adaptive_compile",  "Debug: CUDA Adaptive Compile"),
        ("cycles.debug_use_optix_debug",            "Debug: OptiX Module Debug"),
        ("cycles.debug_use_hip_adaptive_compile",   "Debug: HIP Adaptive Compile"),
        ("cycles.debug_bvh_type",                   "Debug: Viewport BVH Type"),
        ("cycles.direct_light_sampling_type",       "Debug: Direct Light Sampling Type"),
    ] + COMMON_COLOR_MANAGEMENT,

# =============================================================================
# EEVEE ENGINE
# =============================================================================
    "BLENDER_EEVEE": [
    # Sampling:
        # Viewport
        ("eevee.taa_samples",                       "Sampling: Viewport Samples"),
        ("eevee.use_taa_reprojection",              "Sampling: Temporal Reprojection"),
        ("eevee.use_shadow_jitter_viewport",        "Sampling: Jittered Shadows"),
        # Render
        ("eevee.taa_render_samples",                "Sampling: Render Samples" ),
        # Shadows
        ("eevee.use_shadows",                       "Shadows: Use Shadows"),
        ("eevee.shadow_ray_count",                  "Shadows: Shadow Rays"),
        ("eevee.shadow_step_count",                 "Shadows: Shadow Steps"),
        ("eevee.use_volumetric_shadows",            "Shadows: Use Volumetric Shadows"),
        ("eevee.volumetric_shadow_samples",         "Shadows: Volumetric Shadows Steps"),
        ("eevee.shadow_resolution_scale",           "Shadows: Shadow Resolution"),
        # Advanced
        ("eevee.light_threshold",                   "Advanced: Light Threshold"),    
        # Ambient Occlusion         
        ("eevee.use_gtao",                          "Ambient Occlusion: Use Ambient Occlusion"),    # Obsolete  [Should be REMOVED soon] 
        ("eevee.gtao_distance",                     "Ambient Occlusion: Distance"),                 # Obsolete  [Should be REMOVED soon] 
        ("eevee.gtao_factor",                       "Ambient Occlusion: Factor"),                   # Obsolete  [Should be REMOVED soon] 
        ("eevee.gtao_quality",                      "Ambient Occlusion: Quality"),                  # Obsolete  [Should be REMOVED soon] 
        # Bloom              
        ("eevee.use_bloom",                         "Bloom: Use Bloom"),                            # Obsolete  [Should be REMOVED soon] 
        ("eevee.bloom_threshold",                   "Bloom: Threshold"),                            # Obsolete  [Should be REMOVED soon] 
        ("eevee.bloom_knee",                        "Bloom: Knee"),                                 # Obsolete  [Should be REMOVED soon] 
        ("eevee.bloom_radius",                      "Bloom: Radius"),                               # Obsolete  [Should be REMOVED soon] 
        ("eevee.bloom_intensity",                   "Bloom: Intensity"),                            # Obsolete  [Should be REMOVED soon] 
    # Clamping:
        # Surface
        ("eevee.clamp_surface_direct",              "Clamping: Surface Direct Clamp"),
        ("eevee.clamp_surface_indirect",            "Clamping: Surface Indirect Light"),
        # Volume    
        ("eevee.clamp_volume_direct",               "Clamping: Volume Direct Light"),
        ("eevee.clamp_volume_indirect",             "Clamping: Volume Indirect Light"),
        # Intensity
        ("eevee.direct_light_intensity",               "Intensity: Direct Light"),
        ("eevee.indirect_light_intensity",             "Intensity: Indirect Light"),        
    # Raytracing:
        ("eevee.use_raytracing",                                "Raytracing: Use Raytracing"),
        ("eevee.ray_tracing_method",                            "Raytracing: Raytracing Method"),
        ("eevee.ray_tracing_options.resolution_scale",          "Raytracing: Ray Resolution Scale"),
        ("eevee.ray_tracing_options.screen_trace_quality",      "Raytracing: Ray Precision"),
        ("eevee.ray_tracing_options.screen_trace_thickness",    "Raytracing: Ray Thickness"),
        # Denoising
        ("eevee.ray_tracing_options.use_denoise",               "Denoising: Use Denoising"),
        ("eevee.ray_tracing_options.denoise_spatial",           "Denoising: Use Spatial Reuse"),
        ("eevee.ray_tracing_options.denoise_temporal",          "Denoising: Use Temporal Accumulation"),
        ("eevee.ray_tracing_options.denoise_bilateral",         "Denoising: Use Bilateral Filter"),
        # Fast GI Approximation
        ("eevee.ray_tracing_options.trace_max_roughness",       "Fast GI: Threshold"),
        ("eevee.use_fast_gi",                                   "Fast GI: Use Fast GI Approximation"),
        ("eevee.fast_gi_method",                                "Fast GI: Method"),
        ("eevee.fast_gi_resolution",                            "Fast GI: Resolution"),
        ("eevee.fast_gi_ray_count",                             "Fast GI: Ray Count"),
        ("eevee.fast_gi_step_count",                            "Fast GI: Step Count"),
        ("eevee.fast_gi_quality",                               "Fast GI: Quality"),
        ("eevee.fast_gi_distance",                              "Fast GI: Distance"),
        ("eevee.fast_gi_thickness_near",                        "Fast GI: Thickness Near"),
        ("eevee.fast_gi_thickness_far",                         "Fast GI: Thickness Far"),
        ("eevee.fast_gi_bias",                                  "Fast GI: Bias"),
        ("eevee.gi_cubemap_resolution",                         "Fast GI: Cubemap Resolution"), # [ADDED]
        ("eevee.gi_diffuse_bounces",                            "Fast GI: Diffuse Bounces"), # [ADDED]
        ("eevee.gi_glossy_clamp",                               "Fast GI: Glossy Clamp"), # [ADDED]
        ("eevee.gi_visibility_resolution",                      "Fast GI: Visibility Resolution"), # [ADDED]
    # Grease Pencil:
        ("grease_pencil_settings.antialias_threshold",          "Grease Pencil: Anti-aliasing Threshold"),
        ("grease_pencil_settings.antialias_threshold_render",   "Grease Pencil: Render SMAA Threshold"),
        ("grease_pencil_settings.aa_samples",                   "Grease Pencil: Render SSAA Samples"),
        ("grease_pencil_settings.motion_blur_steps",            "Grease Pencil: Motion Blur Steps"),
    # Freestyle:
        ("render.line_thickness_mode",                          "Freestyle: Line Thicknedd Mode"),
        ("render.line_thickness",                               "Freestyle: Line Thinckness"),
    # Volumes:
        ("eevee.volumetric_tile_size",                          "Volume: Resolution"),
        ("eevee.volumetric_samples",                            "Volume: Steps"),
        ("eevee.volumetric_sample_distribution",                "Volume: Distribution"),
        ("eevee.volumetric_ray_depth",                          "Volume: Maximum Depth"),
        ("eevee.volumetric_light_clamp",                        "Volume: Light Clamp"), # [ADDED]
        # Volume Custom Range           
        ("eevee.use_volume_custom_range",                       "Volume: Use Custom Range"),
        ("eevee.volumetric_start",                              "Volume: Start"),
        ("eevee.volumetric_end",                                "Volume: End"),
    # Color Management:         

        # Display           
        ("view_settings.use_hdr_view",                          "Color Management: Use High Dynamic Range"),
        # Curves            
        ("view_settings.use_curve_mapping",                     "Color Management: Use Curves"),
        ("view_settings.curve_mapping",                         "Color Management: Curve Mapping"),
        # White Balance
        ("use_white_balance",                                   "Color Management: Use White Balance"),
        ("scene.view_settings.white_balance_temperature",       "Color Management: White Balance Temperature"),
        ("view_settings.white_balance_tint",                    "Color Management: White Balance Tint"),
    # Curves:   
        ("render.hair_type",                                    "Curves: Curve Shape Type"),
        ("render.hair_subdiv",                                  "Curves: Aditional Curve Subdivision"),
    # Simplify:
        # Simplify Viewport
        ("render.use_simplify",                          "Simplify: Use Simplify"),
        ("render.simplify_subdivision",                  "Simplify: Viewport Max Subdivision"),
        ("render.simplify_child_particles",              "Simplify: Viewport Child Particles"),
        ("cycles.texture_limit",                         "Simplify: Viewport Texture Limit"),
        ("render.simplify_volumes",                      "Simplify: Viewport Volumes"),
        ("render.use_simplify_normals",                  "Simplify: Viewport Normals"),
        # Simplify Render           
        ("render.simplify_subdivision_render",           "Simplify: Render Max Subdivision"),
        ("render.simplify_child_particles_render",       "Simplify: Render Child Particles"),
        ("cycles.texture_limit_render",                  "Simplify: Render Texture Limit"),
        # Culling       
        ("cycles.use_camera_cull",                      "Culling: Use Camera Cull"),
        ("cycles.camera_cull_margin",                   "Culling: Camera Cull Margin"),
        ("cycles.use_distance_cull",                    "Culling: Use Distance Cull"),
        ("cycles.distance_cull_margin",                 "Culling: Distance Cull Margin"),
        # Grease Pencil
        ("render.simplify_gpencil",                     "Simplify: Simplify Grease Pencil"),
        ("render.simplify_gpencil_onplay",              "Simplify: On Play"),
        ("render.simplify_gpencil_view_fill",           "Simplify: Fill"),
        ("render.simplify_gpencil_modifier",            "Simplify: Modifiers"),
        ("render.simplify_gpencil_shader_fx",           "Simplify: Shader FX"),
        ("render.simplify_gpencil_tint",                "Simplify: Tint"),
        ("render.simplify_gpencil_antialiasing",        "Simplify: Anti-Aliasing"),
    # Depth of Field:
        ("eevee.bokeh_max_size",                        "Depth of Field: Maximum Size"),
        ("eevee.bokeh_threshold",                       "Depth of Field: Bokeh Threshold"),
        ("eevee.bokeh_neighbor_max",                    "Depth of Field: Bokeh Neighbor Max"),
        ("eevee.use_bokeh_jittered",                    "Depth of Field: Use Bokeh Jittered"),
        ("eevee.bokeh_overblur",                        "Depth of Field: Bokeh Overblur"),       
    # Motiuon Blur:        
        ("render.use_motion_blur",                      "Motion Blur: Use Motion Blur"),
        ("render.motion_blur_position",                 "Motion Blur: Position"),
        ("render.motion_blur_shutter",                  "Motion Blur: Shutter"),
        ("render.motion_blur_shutter_curve",            "Motion Blur: Shutter Curve"),
        ("eevee.motion_blur_depth_scale",               "Motion Blur: Blending Bias"),
        ("eevee.motion_blur_max",                       "Motion Blur: Maximum Blur"),
        ("eevee.motion_blur_steps",                     "Motion Blur: Steps"),
    # Film:
        ("render.filter_size",                          "Film: Filter Size"),
        ("render.film_transparent",                     "Film: Transparent"),
        ("render.use_overscan",                        "Film: Overscan"), # Obsolete  [Should be REMOVED soon]
        ("eevee.use_overscan",                          "Film: Use Overscan"),
        ("eevee.overscan_size",                         "Film: Overscan Percentage"),
    # Performance:
        ("render.use_high_quality_normals",             "Performance: Use High Quality Normals"),
        # Memory        
        ("eevee.shadow_pool_size",                      "Performance: Shadow Pool"),
        ("eevee.gi_irradiance_pool_size",               "Performance: Light Probes Volume Pool"),
        # Viewport      
        ("render.preview_pixel_size",                   "Performance: Pixel Size"),
        # Compositor        
        ("render.compositor_device",                    "Compositor: Device"),
        ("render.compositor_precision",                 "Compositor: Precision"),
        # Denoise Nodes
        ("render.compositor_denoise_device",            "Performance: Denoise Nodes: Denoising Device"),
        ("render.compositor_denoise_preview_quality",   "Performance: Denoise Nodes: Preview Quality"),
        ("render.compositor_denoise_final_quality",     "Performance: Denoise Nodes: Final Quality"),
    ] + COMMON_COLOR_MANAGEMENT,

# =============================================================================
# WORKBENCH ENGINE
# =============================================================================
    "BLENDER_WORKBENCH": [
    # Grease Pencil:
        ("grease_pencil_settings.antialias_threshold",   "Grease Pencil: Anti-Aliasing Threshold"),
    # Freestyle:
        ("render.use_freestyle",                        "Freestyle: Use Freestyle"),
        ("render.line_thickness_mode",                  "Freestyle: Line Thickness Mode"),
        ("render.line_thickness",                       "Freestyle: Line Thickness"),
    # Color Management: 
    # From unified list
    # Simplify: 
        # Simplify Viewport
        ("render.use_simplify",                     "Simplify: Use Simplify"),
        ("render.simplify_subdivision",             "Simplify: Viewport Max Subdivision"),
        ("render.simplify_child_particles",         "Simplify: Viewport Child Particles"),
        ("render.simplify_volumes",                 "Simplify: Viewport Volumes"),
        ("render.use_simplify_normals",             "Simplify: Viewport Normals"),
        # Simplify Render
        ("render.simplify_subdivision_render",      "Simplify: Render Max Subdivision"),
        ("render.simplify_child_particles_render",  "Simplify: Render Child Particles"),
        # Grease Pencil
        ("render.simplify_gpencil",                 "Simplify: Simplify Grease Pencil"),
        ("render.simplify_gpencil_onplay",          "Simplify: On Play"),
        ("render.simplify_gpencil_view_fill",       "Simplify: Fill"),
        ("render.simplify_gpencil_modifier",        "Simplify: Modifiers"),
        ("render.simplify_gpencil_shader_fx",       "Simplify: Shader FX"),
        ("render.simplify_gpencil_tint",            "Simplify: Tint"),
        ("render.simplify_gpencil_antialiasing",    "Simplify: Anti-Aliasing"),
    # Performance:    
        ("render.use_high_quality_normals",         "Performance: Use High Quality Normals"),
        ("render.compositor_device",                "Performance: Compositor Device"),
        ("render.compositor_precision",             "Performance: Compositor Precision"),
        # Denoise Nodes
        ("render.compositor_denoise_preview_quality",   "Performance: Denoise nodes: Preview Quality"),
        ("render.compositor_denoise_final_quality",     "Performance: Denoise nodes: Final Quality"),
    # Sampling:
        ("display.render_aa",                           "Sampling: Render Anti-Aliasing"),
        ("display.viewport_aa",                         "Sampling: Viewport Anti-Aliasing"),
    # Lighting:
        ("display.shading.light",                               "Shading: Shading Light"),
        ("display.shading.studio_light",                        "Shading: Studio Light"), # [REPLACED]
        ("display.shading.use_world_space_lighting",            "Shading: Use World Space Lighting"),
        ("display.shading.studiolight_rotate_z",                "Shading: Studio Light Rotation"),
        ("display.shading.color_type",                          "Shading: Color"),
        ("display.shading.single_color",                        "Shading: Single Color"),
        ("display.shading.background_type",                     "Shading: Background Type"), # [ADDED]
        ("display.shading.render_pass",                         "Shading: Render Pass"), # [ADDED]
        ("display.shading.studiolight_background_alpha",        "Shading: Studio BG Alpha"), # [ADDED]
        ("display.shading.studiolight_background_blur",         "Shading: Studio BG Blur"), # [ADDED]
        ("display.shading.studiolight_intensity",               "Shading: Studio Intensity"), # [ADDED]
        ("display.shading.type",                                "Shading: Type"), # [ADDED]
        ("display.shading.use_scene_lights",                    "Shading: Use Scene Lights"), # [ADDED]
        ("display.shading.use_scene_lights_render",             "Shading: Use Scene Lights (Rendered)"), # [ADDED]
        ("display.shading.use_scene_world",                     "Shading: Use Scene World"), # [ADDED]
        ("display.shading.use_scene_world_render",              "Shading: Use Scene World (Rendered)"), # [ADDED]
        ("display.shading.use_studiolight_view_rotation",       "Shading: Use View Rotation"), # [ADDED]
        ("display.shading.wireframe_color_type",                "Shading: Wireframe Color"), # [ADDED]
    # Curves:
        ("render.hair_type",        "Curves: Shape"),
        ("render.hair_subdiv",      "Curves: Subdivisions"),
    # Options:
        ("display.shading.show_backface_culling",    "Shading: Backface Culling"),
        ("display.shading.show_xray",                "Shading: Use X-Ray"), # [REPLACED]
        ("display.shading.xray_alpha",               "Shading: X-Ray Alpha"),
        ("display.shading.show_shadows",             "Shading: Use Shadow"),
        ("display.shading.shadow_intensity",         "Shading: Shadow Alpha"),
        ("display.shading.show_xray_wireframe",      "Shading: X-Ray Wireframe"), # [ADDED]
        ("display.shading.xray_alpha_wireframe",     "Shading: X-Ray Wireframe Alpha"), # [ADDED]
        # Cavity
        ("display.shading.show_cavity",             "Shading: Use Cavity"),
        ("display.shading.cavity_type",             "Shading: Cavity Type"),
        # Cavity World Space
        ("display.shading.cavity_ridge_factor",     "Shading: Cavity World Space: Ridge"),
        ("display.shading.cavity_valley_factor",    "Shading: Cavity World Space: Valley"),
        # Cavity Screen Space
        ("display.shading.curvature_ridge_factor",  "Shading: Cavity Screen Space: Ridge"),
        ("display.shading.curvature_valley_factor", "Shading: Cavity Screen Spcae: Valley"),
        ("display.shading.use_dof",                 "Shading: Use Depth of Field"),
        ("display.shading.show_object_outline",     "Shading: Show Object Outline"),
        ("display.shading.object_outline_color",    "Shading: Outline Color"),
        ("display.shading.show_specular_highlight", "Shading: Show Specular Highlight"),
        # Film
        ("render.film_transparent",                 "Film: Transparent"),
    ] + COMMON_COLOR_MANAGEMENT,

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================
    "BLENDER_OUTPUT": [
    # Output Preferences
        ("render.save_output",                  "Output: Save Output"),
    # Format
        ("render.resolution_x",                  "Format: Render Resolution X"),
        ("render.resolution_y",                  "Format: Render Resolution Y"),
        ("render.resolution_percentage",         "Format: Render Resolution Percentage"),
        ("render.pixel_aspect_x",                "Format: Pixel Aspect X"),
        ("render.pixel_aspect_y",                "Format: Pixel Aspect Y"),
        ("render.use_border",                    "Format: Use Render Region"),
        ("render.use_crop_to_border",            "Format: Use Crop to Border"),
        ("render.fps",                           "Format: Frame Rate"),
        ("render.fps_base",                      "Format: Frame Rate Base"),
    # Frame Range           
        ("frame_start",                          "Frame Range: Frame Start"),
        ("frame_end",                            "Frame Range: Frame End"),
        ("frame_step",                           "Frame Range: Frame Step"),
        # Time Stretching           
        ("render.frame_map_old",                 "Time Stretching: Old"),
        ("render.frame_map_new",                 "Time Stretching: New"),
        ("render.ppm_base",                      "Time Stretching: PPM Base"), # [ADDED]
        ("render.ppm_factor",                    "Time Stretching: PPM Factor"), # [ADDED]
    # Stereoscopy   
        ("render.use_multiview",                "Stereoscopy: Use Stereoscopy"),        
        ("render.views_format",                 "Stereoscopy: View Format"),
        ("render.use_spherical_stereo",         "Stereoscopy: Use Spherical Stereo"), # [ADDED]
        ("render.views['left'].use",            "Stereoscopy: Use Left View"),
        ("render.views['left'].file_suffix",    "Stereoscopy: Left Suffix"),
        ("render.views['right'].use",           "Stereoscopy: Use Right View"),
        ("render.views['right'].file_suffix",   "Stereoscopy: Right Suffix"),
    # Output        
        ("render.filepath",                     "Output: File Output Path"),
        ("render.use_file_extension",           "Output: Use File Extensions"),
        ("render.use_render_cache",             "Output: Use Cache Results"),
        ("render.image_settings.file_format",   "Output: File Format"),
        ("render.image_settings.media_type",    "Output: Media Type"), # Blender 5.0
        ("render.image_settings.color_mode",    "Output: Color Mode"),
        ("render.image_settings.color_depth",   "Output: Color Depth"),
        ("render.image_settings.compression",   "Output: Color Compression"),
        ("render.image_settings.quality",       "Output: Quality"), # [ADDED]
        ("render.image_settings.exr_codec",     "Output: EXR Codec"), # [ADDED]
        ("render.image_settings.use_exr_interleave",                            "Output: EXR Interleave"), # [ADDED]
        ("render.image_settings.tiff_codec",                                    "Output: TIFF Codec"), # [ADDED]
        ("render.image_settings.jpeg2k_codec",                                  "Output: JPEG2k Codec"), # [ADDED]
        ("render.image_settings.use_jpeg2k_ycc",                                "Output: JPEG2k YCC"), # [ADDED]
        ("render.image_settings.use_jpeg2k_cinema_preset",                      "Output: JPEG2k Cinema Preset"), # [ADDED]
        ("render.image_settings.use_jpeg2k_cinema_48",                          "Output: JPEG2k Cinema 48"), # [ADDED]
        ("render.image_settings.use_cineon_log",                                "Output: Use Cineon Log"), # [ADDED]
        ("render.image_settings.cineon_black",                                  "Output: Cineon Black"), # [ADDED]
        ("render.image_settings.cineon_gamma",                                  "Output: Cineon Gamma"), # [ADDED]
        ("render.image_settings.cineon_white",                                  "Output: Cineon White"), # [ADDED]
        ("render.image_settings.use_preview",                                   "Output: Use Preview"), # [ADDED]
        ("render.image_settings.has_linear_colorspace",                         "Output: Has Linear Colorspace"), # [ADDED]
        ("render.image_settings.linear_colorspace_settings.is_data",            "Output: Linear Colorspace Is Data"), # [ADDED]
        ("render.image_settings.views_format",                                  "Output: Views Format"), # [ADDED]
        ("render.image_settings.stereo_3d_format.display_mode",                 "Output: Stereo 3D Display Mode"), # [ADDED]
        ("render.image_settings.stereo_3d_format.anaglyph_type",                "Output: Stereo 3D Anaglyph Type"), # [ADDED]
        ("render.image_settings.stereo_3d_format.interlace_type",               "Output: Stereo 3D Interlace Type"), # [ADDED]
        ("render.image_settings.stereo_3d_format.use_interlace_swap",           "Output: Stereo 3D Interlace Swap"), # [ADDED]
        ("render.image_settings.stereo_3d_format.use_sidebyside_crosseyed",     "Output: Stereo 3D Crosseyed"), # [ADDED]
        ("render.image_settings.stereo_3d_format.use_squeezed_frame",           "Output: Stereo 3D Squeezed"), # [ADDED]
        ("render.use_overwrite",                                                "Output: Use Overwrite"), # [REPLACED]
        ("render.use_placeholder",                                              "Output: Use Place Holders"),
    # Color Management
        ("render.image_settings.color_management",                              "Output: Color Management"),
        ("render.image_settings.display_settings.display_device",               "Output: Display Device"),
        ("render.image_settings.view_settings.view_transform",                  "Output: View Transform"),
        ("render.image_settings.view_settings.look",                            "Output: Look"),
        ("render.image_settings.view_settings.exposure",                        "Output: Expossure"),
        ("render.image_settings.view_settings.gamma",                           "Output: Gamma"),
        ("render.image_settings.view_settings.use_curve_mapping",               "Output: Use Curve Mapping"),
        ("render.image_settings.view_settings.use_white_balance",               "Output: Use White Balance"), 
        ("render.image_settings.view_settings.white_balance_temperature",       "Output: White Balance Temp"),
        ("render.image_settings.view_settings.white_balance_tint",              "Output: White Balance Tint"),
        ("render.image_settings.display_settings.emulation",                    "Output: Emulation"),           #
        ("render.image_settings.view_settings.curve_mapping",                   "Output: Curve Mapping"),       #
        ("render.image_settings.view_settings.is_hdr",                          "Output: Is HDR"),              #
        ("render.image_settings.view_settings.support_emulation",               "Output: Supports Emulation"),  #
        ("render.image_settings.linear_colorspace_settings.name",               "Output: Color Space"),         ## Only Visible when the Image Type is EXR
    # Metadata:                                                     
        ("render.metadata_input",              "Metadata: Metadata Input"),
        ("render.use_stamp_date",              "Metadata: Stamp Date"),
        ("render.use_stamp_time",              "Metadata: Stamp Time"),
        ("render.use_stamp_render_time",       "Metadata: Stamp Render Time"),
        ("render.use_stamp_frame",             "Metadata: Stamp Frame"),
        ("render.use_stamp_frame_range",       "Metadata: Stamp Frame Range"),
        ("render.use_stamp_memory",            "Metadata: Stamp Memory"),
        ("render.use_stamp_hostname",          "Metadata: Stamp Hostname"),
        ("render.use_stamp_camera",            "Metadata: Stamp Camera"),
        ("render.use_stamp_lens",              "Metadata: Stamp Lens"),
        ("render.use_stamp_scene",             "Metadata: Stamp Scene"),
        ("render.use_stamp_marker",            "Metadata: Stamp Marker"),
        ("render.use_stamp_filename",          "Metadata: Stamp Filename"),
        ("render.use_stamp_sequencer_strip",   "Metadata: Stamp Sequence Strip"),
        ("render.use_stamp_note",              "Metadata: Use Notes"),
        ("render.stamp_note_text",             "Metadata: Stamp Note Text"),
        ("render.use_stamp",                   "Metadata: Use Burn Into Image"),
        ("render.stamp_font_size",             "Metadata: Stamp Font Size"),
        ("render.stamp_foreground",            "Metadata: Stamp Text Color"),
        ("render.stamp_background",            "Metadata: Stamp Background Color"),
        ("render.use_stamp_labels",            "Metadata: Stamp: Include Labels"),
    # Post Processing
        ("render.use_compositing",                          "Post Processing: Use Post Processing"),
        ("render.use_sequencer",                            "Post Processing: Use Render Sequence"),
        ("render.sequencer_gl_preview",                     "Post Processing: Sequencer GL Preview"), # [ADDED]
        ("render.use_sequencer_override_scene_strip",       "Post Processing: Override Scene Strip"), # [ADDED]
        ("render.dither_intensity",                         "Post Processing: Dither"),
    # Encoding (for video formats)
        ("render.ffmpeg.format",               "Encoding: Container"),
        ("render.ffmpeg.use_autosplit",        "Encoding: Use Autosplit"),
        # Video
        ("render.ffmpeg.codec",                "Encoding: Video Codec"),
        ("render.ffmpeg.use_lossless_output",  "Encoding: Use Lossless Output"),
        ("render.ffmpeg.ffmpeg_prores_profile","Encoding: ProRes Profile"),
        ("render.ffmpeg.constant_rate_factor", "Encoding: Constant Rate Factor"),
        ("render.ffmpeg.ffmpeg_preset",        "Encoding: Encoding Speed"),
        ("render.ffmpeg.gopsize",              "Encoding: GOP Size"),
        ("render.ffmpeg.use_max_b_frames",     "Encoding: Use Max B-Frames"),
        ("render.ffmpeg.max_b_frames",         "Encoding: Max B-Frames"),
        ("render.ffmpeg.video_bitrate",        "Encoding: Video Bitrate"),
        ("render.ffmpeg.minrate",              "Encoding: Minrate"),
        ("render.ffmpeg.maxrate",              "Encoding: Maxrate"),
        ("render.ffmpeg.buffersize",           "Encoding: Buffer Size"),
        ("render.ffmpeg.muxrate",              "Encoding: Mux Rate"),
        ("render.ffmpeg.packetsize",           "Encoding: Mux Packet Size"),
        ("render.ffmpeg.custom_constant_rate_factor",           "Encoding: Constant Rate Factor"),
        # Audio
        ("render.ffmpeg.audio_codec",          "Encoding: Audio Codec"),
        ("render.ffmpeg.audio_channels",       "Encoding: Audio Channels"),
        ("render.ffmpeg.audio_mixrate",        "Encoding: Audio Sample Rate"),
        ("render.ffmpeg.audio_bitrate",        "Encoding: Audio Bitrate"),
        ("render.ffmpeg.audio_volume",         "Encoding: Audio Volume"),
        ] + OCTANE_OUTPUT_PROPS, 

    "BLENDER_VIEW_LAYER": [ 
    # View Layer
    # Passes
        # Data    
        ("<ACTIVE_VIEW_LAYER>.use_pass_combined",                   "Data Pass: Combined"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_z",                          "Data Pass: Depth Z"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_mist",                       "Data Pass: Mist"),
        ("world.mist_settings.start",                               "Mist Pass: Start"),
        ("world.mist_settings.depth",                               "Mist Pass: Depth"),
        ("world.mist_settings.falloff",                             "Mist Pass: Falloff"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_position",                   "Data Pass: Position"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_normal",                     "Data Pass: Normal"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_vector",                     "Data Pass: Vector"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_uv",                         "Data Pass: UV"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_grease_pencil",              "Data Pass: Grease Pencil"),
        ("<ACTIVE_VIEW_LAYER>.cycles.denoising_store_passes",       "Data Pass: Denoising Data"),
        # Indexes
        ("<ACTIVE_VIEW_LAYER>.use_pass_object_index",               "Data Pass: Object Index"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_material_index",             "Data Pass: Material Index"),
        # Debug
        ("<ACTIVE_VIEW_LAYER>.cycles.pass_debug_sample_count",      "Data Pass: Sample Count"),
        ("<ACTIVE_VIEW_LAYER>.cycles.pass_render_time",             "Data Pass: Render Time"),
        # Alpha Threshold
        ("<ACTIVE_VIEW_LAYER>.pass_alpha_threshold",                "Data Pass: Alpha Threshold"),
    # Light
        # Diffuse
        ("<ACTIVE_VIEW_LAYER>.use_pass_diffuse_direct",             "Diffuse Pass: Direct"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_diffuse_indirect",           "Diffuse Pass: Indirect"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_diffuse_color",              "Diffuse Pass: Color"),
        # Glossy
        ("<ACTIVE_VIEW_LAYER>.use_pass_glossy_direct",              "Glossy Pass: Direct"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_glossy_indirect",            "Glossy Pass: Indirect"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_glossy_color",               "Glossy Pass: Color"),
        # Transmission
        ("<ACTIVE_VIEW_LAYER>.use_pass_transmission_direct",        "Transmission Pass: Direct"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_transmission_indirect",      "Transmission Pass: Indirect"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_transmission_color",         "Transmission Pass: Color"),
        # Volume
        ("<ACTIVE_VIEW_LAYER>.cycles.use_pass_volume_direct",       "Volume Pass: Direct"),
        ("<ACTIVE_VIEW_LAYER>.cycles.use_pass_volume_indirect",     "Volume Pass: Indirect"),
        ("<ACTIVE_VIEW_LAYER>.eevee.use_pass_volume_direct",        "Volume Pass: Light"),
        ("<ACTIVE_VIEW_LAYER>.cycles.use_pass_volume_scatter",      "Volume Pass: Scatter"),
        ("<ACTIVE_VIEW_LAYER>.cycles.use_pass_volume_transmit",     "Volume Pass: Transmit"),
        ("<ACTIVE_VIEW_LAYER>.cycles.use_pass_volume_majorant",     "Volume Pass: Majorant"),
        # Other 
        ("<ACTIVE_VIEW_LAYER>.use_pass_emit",                       "Other Passes: Emission"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_environment",                "Other Passes: Environment"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_ambient_occlusion",          "Other Passes: Ambient Occlusion"),
        ("<ACTIVE_VIEW_LAYER>.cycles.use_pass_shadow_catcher",      "Other Passes: Shadow Cather"),
        ("<ACTIVE_VIEW_LAYER>.eevee.use_pass_transparent",          "Other Passes: Transparent"),
        ("eevee.gtao_distance",                                     "Other Passes: Occlusion Distance"), # Obsolete  [Should be REMOVED soon]
    # Cryptomatte
        ("<ACTIVE_VIEW_LAYER>.use_pass_cryptomatte_object",         "Cryptomatte Pass: Object"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_cryptomatte_material",       "Cryptomatte Pass: Material"),
        ("<ACTIVE_VIEW_LAYER>.use_pass_cryptomatte_asset",          "Cryptomatte Pass: Asset"),
        ("<ACTIVE_VIEW_LAYER>.pass_cryptomatte_depth",              "Cryptomatte Pass: Levels"),
    # Filter
        ("<ACTIVE_VIEW_LAYER>.use_sky",           "Filter: Use Sky"),
        ("<ACTIVE_VIEW_LAYER>.use_solid",         "Filter: use Solid"),
        ("<ACTIVE_VIEW_LAYER>.use_strand",        "Filter: Use Strand"),
        ("<ACTIVE_VIEW_LAYER>.use_volumes",       "Filter: Use Volumes"),
        ("<ACTIVE_VIEW_LAYER>.use_motion_blur",   "Filter: Use Motion Blur"),
    ], 

# =============================================================================
# SCENE PROPERTIES
# =============================================================================
    "BLENDER_SCENE": [ 
    # Units
        ("unit_settings.system",            "Scene Units: System"),
        ("unit_settings.scale_length",      "Scene Units: Scale"),
        ("unit_settings.use_separate",      "Scene Units: Separate Units"),
        ("unit_settings.system_rotation",   "Scene Units: Rotation"),
        ("unit_settings.length_unit",       "Scene Units: Length"),
        ("unit_settings.mass_unit",         "Scene Units: Mass"),
        ("unit_settings.time_unit",         "Scene Units: Time"),
        ("unit_settings.temperature_unit",  "Scene Units: Temperature"),
        # Gravity
        ("use_gravity",                     "Gravity: Use Gravity"),
        ("gravity",                         "Gravity: Gravity"),
        ],

# =============================================================================
# OCTANE RENDER PROPERTIES
# =============================================================================
    "OCTANE": [
    # SIMPLIFY
        ("render.use_simplify",                     "Simplify: Use Simplify"),
        # SIMPLIFY ViewportT
        ("render.simplify_subdivision",             "Simplify: Viewport Max Subdvision"),
        ("render.simplify_child_particles",         "Simplify: TMax Child Particles"),
        ("render.simplify_volumes",                 "Simplify: Volume Resolution"),
        ("render.use_simplify_normals",             "Simplify: NormalsT"),
        # SIMPLIFY Render
        ("render.simplify_subdivision_render",       "Simplify: Render Max Subdivision"),
        ("render.simplify_child_particles_render",   "Simplify: Max Child Particles"),
        # SIMPLIFY Grease Pencil
        ("render.simplify_gpencil",                  "Simplify: Use Simplify Greas Pencil"),
        ("render.simplify_gpencil_onplay",           "Simplify: Playback Only"),
        ("render.simplify_gpencil_view_fill",        "Simplify: Fill"),
        ("render.simplify_gpencil_modifier",         "Simplify: Modifiers"),
        ("render.simplify_gpencil_shader_fx",        "Simplify: Shader Effects"),
        ("render.simplify_gpencil_tint",             "Simplify: Layers Tinting"),
        ("render.simplify_gpencil_antialiasing",     "Simplify: Antialiasing"),

    # Kernel
        # --- O TIPO DE KERNEL (Sempre deve ser o primeiro) ---
        ("KTOOLS_SPECIAL.octane_active_kernel", "Kernel: Active Engine"),
        
        # --- COMUNS A QUASE TODOS OS KERNELS ---
        ("KTOOLS_SPECIAL.octane_kernel_input|Max. samples",             "Kernel: Max Samples"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Max. preview samples",     "Kernel: Max Preview Samples"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Diffuse depth",            "Kernel: Diffuse Depth"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Specular depth",           "Kernel: Specular Depth"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Scatter depth",            "Kernel: Scatter Depth"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Ray epsilon",              "Kernel: Ray Epsilon"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Filter size",              "Kernel: Filter Size"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Alpha shadows",            "Kernel: Alpha Shadows"),
        ("KTOOLS_SPECIAL.octane_kernel_input|GI clamp",                 "Kernel: GI Clamp"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Alpha channel",            "Kernel: Alpha Channel"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Keep environment",         "Kernel: Keep Environment"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Parallel samples",         "Kernel: Parallel Samples"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Max. tile samples",        "Kernel: Max Tile Samples"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Minimize net traffic",     "Kernel: Minimize Net Traffic"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Deep image",               "Kernel: Deep Image"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Deep render AOVs",         "Kernel: Deep Render AOVs"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Max. depth samples",       "Kernel: Max Depth Samples"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Depth tolerance",          "Kernel: Depth Tolerance"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Toon shadow ambient",      "Kernel: Toon Shadow Ambient"),
        
        # --- DIRECT LIGHTING / PATH TRACING / PMC ESPECÍFICOS ---
        ("KTOOLS_SPECIAL.octane_kernel_input|Global illumination mode",     "Kernel: Global Illumination Mode"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Glossy depth",                 "Kernel: Glossy Depth"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Maximal overlapping volumes",  "Kernel: Maximal Overlapping Volumes"),
        ("KTOOLS_SPECIAL.octane_kernel_input|AO distance",                  "Kernel: AO Distance"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Nested dielectrics",           "Kernel: Nested Dielectrics"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Irradiance mode",              "Kernel: Irradiance Mode"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Max subdivision level",        "Kernel: Max Subdivision Level"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Caustic blur",                 "Kernel: Caustic Blur"),
        ("KTOOLS_SPECIAL.octane_kernel_input|AI light",                     "Kernel: AI Light"),
        ("KTOOLS_SPECIAL.octane_kernel_input|AI light update",              "Kernel: AI Light Update"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Light IDs action",             "Kernel: Light IDs Action"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Path term. power",             "Kernel: Path Term Power"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Direct light rays",            "Kernel: Direct Light Rays"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Coherent ratio",               "Kernel: Coherent Ratio"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Static noise",                 "Kernel: Static Noise"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Adaptive sampling",            "Kernel: Adaptive Sampling"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Noise threshold",              "Kernel: Noise Threshold"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Min. adaptive samples",        "Kernel: Min Adaptive Samples"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Pixel grouping",               "Kernel: Pixel Grouping"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Expected exposure",            "Kernel: Expected Exposure"),
        ("KTOOLS_SPECIAL.octane_kernel_input|White light spectrum",         "Kernel: White Light Spectrum"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Direct light importance",      "Kernel: Direct Light Importance"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Max. rejects",                 "Kernel: Max Rejects"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Work chunk size",              "Kernel: Work Chunk Size"),
        
        # --- INFO CHANNELS ESPECÍFICOS ---
        ("KTOOLS_SPECIAL.octane_kernel_input|Type",                             "Kernel: Info Channel Type"),
        ("KTOOLS_SPECIAL.octane_kernel_input|AO alpha shadows",                 "Kernel: AO Alpha Shadows"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Opacity threshold",                "Kernel: Opacity Threshold"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Maximum Z-depth",                  "Kernel: Maximum Z-Depth"),
        ("KTOOLS_SPECIAL.octane_kernel_input|UV max",                           "Kernel: UV Max"),
        ("KTOOLS_SPECIAL.octane_kernel_input|UV coordinate selection",          "Kernel: UV Coordinate Selection"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Max speed",                        "Kernel: Max Speed"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Sampling mode",                    "Kernel: Sampling Mode"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Bump and normal mapping",          "Kernel: Bump And Normal Mapping"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Wireframe backface highlighting",  "Kernel: Wireframe Backface Highlighting"),
        
        # --- PHOTON TRACING ESPECÍFICOS ---
        ("KTOOLS_SPECIAL.octane_kernel_input|Photon depth",                 "Kernel: Photon Depth"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Accurate colors",              "Kernel: Accurate Colors"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Photon gathering radius",      "Kernel: Photon Gathering Radius"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Photon count multiplier",      "Kernel: Photon Count Multiplier"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Photon gather samples",        "Kernel: Photon Gather Samples"),
        ("KTOOLS_SPECIAL.octane_kernel_input|Exploration strength",         "Kernel: Exploration Strength"),
        
        # --- DEPRECATED (Mantidos por retrocompatibilidade) ---
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]Affect roughness",             "Kernel: [Deprecated] Affect Roughness"),
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]AI light strength",            "Kernel: [Deprecated] AI Light Strength"),
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]Analytic light",               "Kernel: [Deprecated] Analytic Light"),
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]Adaptive strength",            "Kernel: [Deprecated] Adaptive Strength"),
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]Use old color pipeline",       "Kernel: [Deprecated] Use Old Color Pipeline"),
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]Coherent mode",                "Kernel: [Deprecated] Coherent Mode"),
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]RR probability",               "Kernel: [Deprecated] RR Probability"),
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]Emulate old volume behavior",  "Kernel: [Deprecated] Emulate Old Volume Behavior"),
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]Distributed ray tracing",      "Kernel: [Deprecated] Distributed Ray Tracing"),
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]AO alpha shadows",             "Kernel: [Deprecated] AO Alpha Shadows"),
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]Path depth",                   "Kernel: [Deprecated] Path Depth"),
        ("KTOOLS_SPECIAL.octane_kernel_input|[Deprecated]Exploration strength",         "Kernel: [Deprecated] Exploration Strength"),

    # Octane Motion Blur
        ("render.use_motion_blur",                                      "Motion Blur: Use Motion Blur"),
        ("octane.animation_settings.mb_direction",                      "Motion Blur: Shutter alignment"),
        ("octane.animation_settings.shutter_time",                      "Motion Blur: Shutter time"),
        ("octane.animation_settings.subframe_start",                    "Motion Blur: Subframe start"),
        ("octane.animation_settings.subframe_end",                      "Motion Blur: Subframe end"),
        ("octane.animation_settings.emulate_old_motion_blur_behavior",  "Motion Blur: Old motion blur behavior"),
        ("octane.animation_settings.clamp_motion_blur_data_source",     "Motion Blur: Auto Clamp Mode"),
    # Octane Server
        ("octane.resource_cache_type",                      "Server: Resourse Cache Type"),
        ("octane.dirty_resource_detection_strategy_type",   "Server: Dirty Resource Detection Strategy Type"),
        ("octane.meshes_type",                              "Server: Render All Meshes As"),
        ("octane.enable_realtime",                          "Server: Enable Real-time Viewport Rendering"),
        ("octane.prefer_image_type",                        "Server: Final Render Image"),
        ("octane.maximize_instancing",                      "Server: Maximaze Instancing"),
        ("octane.clay_mode",                                "Server: Clay mode"),
        ("octane.priority_mode",                            "Server: Render priority"),
        ("octane.subsample_mode",                           "Server: Subsample mode"),
        # This section has 7 operators
    # Octane Out of Core
        ("octane.out_of_core_enable",               "Out Of Core: Enable Out of Core"),
        ("octane.out_of_core_limit",                "Out Of Core: Out of Core Memory Limit (MB)"),
        ("octane.out_of_core_gpu_headroom",         "Out Of Core: GPU Headroom (MB)"),
    # Grease Pencil
        ("grease_pencil_settings.antialias_threshold",            "Grease Pencil: Anti-aliasing Threshold"),
    # Freestyle
        ("render.use_freestyle",            "Freestyle: Enable Freestyle"),
        ("render.line_thickness_mode",      "Freestyle: Line Thickness Mode"),
        ("render.line_thickness",           "Freestyle: Line Thickness"),
    # Color Management
        # It is added  after the render list
    ] + COMMON_COLOR_MANAGEMENT,

    "OCTANE_VIEW_LAYER": [
    # View Layer
        ("view_layers<ACTIVE_VIEW_LAYER>.use", "View Layer: Use for Rendering"),
        ("render.use_single_layer",            "View Layer: Render Single Layer"),
    # Octane Render Layers
        #("PROPERTY",            "NAME"),
        #("PROPERTY",            "NAME"),
        #("PROPERTY",            "NAME"),
        #("PROPERTY",            "NAME"),
    # Octane Render Layers Global
        ("octane.render_layer.layers_enable",   "Render Layer Global: Enable Octane Render Layers(Global)"),
        ("octane.render_layer.layers_mode",     "Render Layer Global: Mode"),
        ("octane.render_layer.layers_current",  "Render Layer Global: Active Layer ID"),
        ("octane.render_layer.layers_invert",   "Render Layer Global: Invert"),
    # Passes
        # Beauty Passes
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_beauty",          "Beauty Pass: Beauty"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_emitters",        "Beauty Pass: Emitters"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_env",             "Beauty Pass: Environment"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_sss",             "Beauty Pass: SSS"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_shadow",          "Beauty Pass: Shaow"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_irradiance",      "Beauty Pass: Irradiance"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir",       "Beauty Pass: LightDir"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_noise",           "Beauty Pass: Noise"),
        # Beauty Diffuse
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_diff",            "Beauty Pass: Diffuse"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_diff_dir",        "Beauty Pass: Diffuse Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_diff_indir",      "Beauty Pass: Diffuse Indirect"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_diff_filter",     "Beauty Pass: Diffuse Filter"),
        # Beauty Reflection
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_reflect",             "Beauty Pass: Reflection"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_reflect_dir",         "Beauty Pass: Reflection Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_reflect_indir",       "Beauty Pass: Reflection Indirect"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_reflect_filter",      "Beauty Pass: Reflection Filter"),
        # Beauty Refraction
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_beauty",              "Beauty Pass: Refraction"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_refract_filter",      "Beauty Pass: Refraction Filter"),
        # Beauty Transmission
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_transm",              "Beauty Pass: Transmission"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_transm_filter",       "Beauty Pass: Transmission Filter"),
        # Beauty Volume
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_volume",              "Beauty Pass: Volume"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_vol_mask",            "Beauty Pass: Volume Mask"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_vol_emission",        "Beauty Pass: Volume Emission"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_vol_z_front",         "Beauty Pass: Volume ZFront"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_vol_z_back",          "Beauty Pass: Volume ZBack"),
        # Beauty Transmission
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_denoise_albedo",      "Beauty Pass: Denoise Albedo"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_denoise_normal",      "Beauty Pass: Denoise Normal"),
    # Denoiser Passes
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_denoise_beauty",          "Denoiser Pass: Beauty"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_denoise_diff_dir",        "Denoiser Pass: DiffDir"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_denoise_diff_indir",      "Denoiser Pass: DiffIndir"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_denoise_reflect_dir",     "Denoiser Pass: ReflectDir"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_denoise_reflect_indir",   "Denoiser Pass: ReflectIndir"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_denoise_remainder",       "Denoiser Pass: Refraction"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_denoise_vol",             "Denoiser Pass: Volume"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_denoise_vol_emission",    "Denoiser Pass: VolEmission"),
    # Post Processing Passes
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_postprocess",             "Post Processing Pass: Post processing"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_postfxmedia",             "Post Processing Pass: Postfix media"),
        ("<ACTIVE_VIEW_LAYER>.octane.pass_pp_env",                      "Post Processing Pass: Include environment"),
    # Render Layer
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_layer_shadows",           "Render Layer Pass: Shadow"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_layer_black_shadow",      "Render Layer Pass: BlackShadow"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_layer_reflections",       "Render Layer Pass: Reflections"),
    # Light Passes
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_ambient_light", "Light Pass: Ambient"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_ambient_light_dir", "Light Pass: Ambient Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_ambient_light_indir", "Light Pass: Ambient Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_sunlight", "Light Pass: Sunlight"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_sunlight_dir", "Light Pass: Sunlight Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_sunlight_indir", "Light Pass: Sunlight Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_1", "Light Pass: 1"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_1", "Light Pass: 1 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_1", "Light Pass: 1 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_2", "Light Pass: 2"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_2", "Light Pass: 2 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_2", "Light Pass: 2 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_3", "Light Pass: 3"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_3", "Light Pass: 3 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_3", "Light Pass: 3 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_4", "Light Pass: 4"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_4", "Light Pass: 4 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_4", "Light Pass: 4 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_5", "Light Pass: 5"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_5", "Light Pass: 5 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_5", "Light Pass: 5 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_6", "Light Pass: 6"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_6", "Light Pass: 6 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_6", "Light Pass: 6 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_7", "Light Pass: 7"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_7", "Light Pass: 7 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_7", "Light Pass: 7 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_8", "Light Pass: 8"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_8", "Light Pass: 8 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_8", "Light Pass: 8 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_9", "Light Pass: 9"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_9", "Light Pass: 9 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_9", "Light Pass: 9 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_10", "Light Pass: 10"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_10", "Light Pass: 10 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_10", "Light Pass: 10 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_11", "Light Pass: 11"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_11", "Light Pass: 11 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_11", "Light Pass: 11 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_12", "Light Pass: 12"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_12", "Light Pass: 12 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_12", "Light Pass: 12 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_13", "Light Pass: 13"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_13", "Light Pass: 13 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_13", "Light Pass: 13 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_14", "Light Pass: 14"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_14", "Light Pass: 14 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_14", "Light Pass: 14 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_15", "Light Pass: 15"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_15", "Light Pass: 15 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_15", "Light Pass: 15 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_16", "Light Pass: 16"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_16", "Light Pass: 16 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_16", "Light Pass: 16 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_17", "Light Pass: 17"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_17", "Light Pass: 17 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_17", "Light Pass: 17 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_18", "Light Pass: 18"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_18", "Light Pass: 18 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_18", "Light Pass: 18 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_19", "Light Pass: 19"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_19", "Light Pass: 19 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_19", "Light Pass: 19 Indirect"),
        
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_pass_20", "Light Pass: 20"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_dir_pass_20", "Light Pass: 20 Direct"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_light_indir_pass_20", "Light Pass: 20 Indirect"),
    # Cryptomatte
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_crypto_instance_id",      "Cryptomatte Pass: InstanceID"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_crypto_mat_node_name",    "Cryptomatte Pass: MatNodeName"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_crypto_mat_node",         "Cryptomatte Pass: MatNode"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_crypto_mat_pin_node",     "Cryptomatte Pass: MatPinNode"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_crypto_obj_node_name",    "Cryptomatte Pass: ObjNodeName"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_crypto_obj_node",         "Cryptomatte Pass: ObjNode"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_crypto_obj_pin_node",     "Cryptomatte Pass: ObjPinNode"),
        ("<ACTIVE_VIEW_LAYER>.octane.cryptomatte_pass_channels",        "Cryptomatte Pass: Number of Channels"),
    # Info Passes
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_z_depth",                "Info Pass: Z-Depth"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_position",               "Info Pass: Position"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_uv",                     "Info Pass: UV"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_tex_tangent",            "Info Pass: Texture Tangent"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_motion_vector",          "Info Pass: Motion Vector"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_mat_id",                 "Info Pass: Material ID"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_obj_id",                 "Info Pass: Object ID"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_obj_layer_color",        "Info Pass: Object Layer Color"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_baking_group_id",        "Info Pass: Baking Group ID"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_light_pass_id",          "Info Pass: Light Pass ID"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_render_layer_id",        "Info Pass: Render Layer ID"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_render_layer_mask",      "Info Pass: Render Layer Mask"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_wireframe",              "Info Pass: Wireframe"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_ao",                     "Info Pass: Ambient Occlusion"),
        # Normals
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_geo_normal",             "Info Pass: Normal Geometric"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_smooth_normal",          "Info Pass: Normal Smooth"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_shading_normal",         "Info Pass: Normal Shading"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_info_tangent_normal",         "Info Pass: Normal Tangent"),
        # Settings
        ("<ACTIVE_VIEW_LAYER>.octane.info_pass_max_samples",                "Info Pass: Max Samples"),
        ("<ACTIVE_VIEW_LAYER>.octane.info_pass_sampling_mode",              "Info Pass: Sampling Mode"),
        ("<ACTIVE_VIEW_LAYER>.octane.info_pass_opacity_threshold",          "Info Pass: Opacity Threshold"),
        ("<ACTIVE_VIEW_LAYER>.octane.info_pass_z_depth_max",                "Info Pass: Z-Depth Max"),
        ("<ACTIVE_VIEW_LAYER>.octane.info_pass_uv_max",                     "Info Pass: UV Max"),
        ("<ACTIVE_VIEW_LAYER>.octane.info_pass_uv_coordinate_selection",    "Info Pass: UV Coordinate Selection"),
        ("<ACTIVE_VIEW_LAYER>.octane.info_pass_max_speed",                  "Info Pass: Max Speed"),
        ("<ACTIVE_VIEW_LAYER>.octane.info_pass_ao_distance",                "Info Pass: AO Distance"),
        ("<ACTIVE_VIEW_LAYER>.octane.info_pass_alpha_shadows",              "Info Pass: Alpha Shadows"),
        ("<ACTIVE_VIEW_LAYER>.octane.info_pass_bump",                       "Info Pass: Bump"),
        ("<ACTIVE_VIEW_LAYER>.octane.shading_enabled",                      "Info Pass: Shading Enabled"),
        ("<ACTIVE_VIEW_LAYER>.octane.highlight_backfaces",                  "Info Pass: Highlight Backfaces"),
    # Material Passes
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_mat_opacity",                     "Material Pass: Opacity"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_mat_roughness",                   "Material Pass: Routhness"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_mat_ior",                         "Material Pass: IOR"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_mat_diff_filter_info",            "Material Pass: Transmission"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_mat_reflect_filter_info",         "Material Pass: Info Diffuse"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_mat_refract_filter_info",         "Material Pass: Info Refraction"),
        ("<ACTIVE_VIEW_LAYER>.octane.use_pass_mat_transm_filter_info",          "Material Pass: Info Transmission")
    ],

    "OCTANE_IMAGER": [ 
    # IMAGER
        ("octane.use_preview_setting_for_camera_imager",        "Imager: Use Imager for all Cameras"),
        # PREVIEW MODE
        ("octane.use_preview_camera_imager",                    "Imager: Preview Mode"),
        ("oct_view_cam.imager.exposure",                        "Imager: TExposure"),
        ("oct_view_cam.imager.hotpixel_removal",                "Imager: Hotpixel removal"),
        ("oct_view_cam.imager.vignetting",                      "Imager: Vignetting"),
        ("oct_view_cam.imager.white_balance",                   "Imager:White balance "),
        ("oct_view_cam.imager.saturation",                      "Imager: Saturation"),
        ("oct_view_cam.imager.disable_partial_alpha",           "Imager: Disable partial alpha"),
        ("oct_view_cam.imager.dithering",                       "Imager: Dithering"),
        ("oct_view_cam.imager.min_display_samples",             "Imager: Min. display samples"),
        ("oct_view_cam.imager.max_tonemap_interval",            "Imager: Max. tonemap interval"),
        # OCIO
        ("oct_view_cam.imager.ocio_view",            "OCIO: OCIO view"),
        ("oct_view_cam.imager.ocio_look",            "OCIO: OCIO look"),
        ("oct_view_cam.imager.force_tone_mapping",   "OCIO: Force tone mapping"),
        # Tone Mapping
        ("oct_view_cam.imager.aces_tone_mapping",               "Tone Mapping: ACES tone mapping"),
        ("oct_view_cam.imager.highlight_compression",           "Tone Mapping: Highlight compression"),
        ("oct_view_cam.imager.saturate_to_white",               "Tone Mapping: Clip to white"),
        ("oct_view_cam.imager.order",                           "Tone Mapping: Order"),
        ("oct_view_cam.imager.viewport_response_type",          "Tone Mapping: Response curve"),
        ("oct_view_cam.imager.neutral_response",                "Tone Mapping: Neutral response"),
        ("oct_view_cam.imager.gamma",                           "Tone Mapping: Gamma"),
        ("oct_view_cam.imager.custom_lut",                      "Tone Mapping: Custom LUT"),
        ("oct_view_cam.imager.lut_strength",                    "Tone Mapping: LUT Strength"),
        # Denoiser
        ("oct_view_cam.imager.denoiser",                    "Denoiser: Use Denoiser"),
        ("oct_view_cam.imager.denoiser_type",               "Denoiser: Type"),
        ("oct_view_cam.imager.denoise_volume",              "Denoiser: Denoise volumes"),
        ("oct_view_cam.imager.denoise_prefilter",           "Denoiser: Prefilter auxiliary AOVs"),
        ("oct_view_cam.imager.denoise_once",                "Denoiser: Denoise on completion"),
        ("oct_view_cam.imager.min_denoise_samples",         "Denoiser: Min. denoiser samples"),
        ("oct_view_cam.imager.max_denoise_interval",        "Denoiser: Max. denoiser interval"),
        ("oct_view_cam.imager.denoiser_original_blend",     "Denoiser: Blend"),
        # Upsampler
        ("oct_view_cam.imager.up_sample_mode",                      "Upsampler: Mode"),
        ("oct_view_cam.imager.enable_ai_up_sampling",               "Upsampler: Enable AI up-sampling"),
        ("oct_view_cam.imager.up_sampling_on_completion",           "Upsampler: Up-sampling on completion"),
        ("oct_view_cam.imager.min_up_sampler_samples",              "Upsampler: Min. up-sampler samples"),
    ],

    "OCTANE_POST": [ 
    # Post Image Processing
        ("octane.use_preview_post_process_setting",          "Postprocess: Use for all Cameras"),
        # Post Image Processing
        ("oct_view_cam.postprocess",                         "Postprocess: Use Postprocess Preview Mode"),
        ("oct_view_cam.post_processing.cutoff",              "Postprocess: cutoff"),
        ("oct_view_cam.post_processing.bloom_power",         "Postprocess: Bloom power"),
        ("oct_view_cam.post_processing.glare_power",         "Postprocess: Glare power"),
        ("oct_view_cam.post_processing.glare_ray_amount",    "Postprocess: Glare ray count"),
        ("oct_view_cam.post_processing.glare_angle",         "Postprocess: Glare angle"),
        ("oct_view_cam.post_processing.glare_blur",          "Postprocess: Glare blur"),
        ("oct_view_cam.post_processing.scale_with_film",     "Postprocess: Scale with film"),
        ("oct_view_cam.post_processing.spread_start",        "Postprocess: Spread start"),
        ("oct_view_cam.post_processing.spread_start",        "Postprocess: Spread start"),
        ("oct_view_cam.post_processing.spread_end",          "Postprocess: Spread end"),
        ("oct_view_cam.post_processing.spectral_intencity",  "Postprocess: Spectral intensity"),
        ("oct_view_cam.post_processing.spectral_shift",      "Postprocess: Spectral shift"),
        # fect
        ("oct_view_cam.post_processing.chromatic_aberration_intensity",      "Lens Effect: Chromatic aberration intensity"),
        ("oct_view_cam.post_processing.lens_flare",                          "Lens Effect: Lens flare intensity"),
        ("oct_view_cam.post_processing.lens_flare_extent",                   "Lens Effect: Lens flare extent"),
        # Post Processing Volume Effects
        ("oct_view_cam.post_processing.light_beams",                                 "Postprocess: Light bearns"),
        ("oct_view_cam.post_processing.medium_density_for_postfx_light_beams",       "Postprocess: Medium density for postfx light beams"),
        ("oct_view_cam.post_processing.enable_fog",                                  "Postprocess: Fog"),
        ("oct_view_cam.post_processing.fog_extinction_distance",                     "Postprocess: Fog extinction distance"),
        ("oct_view_cam.post_processing.fog_base_level",                              "Postprocess: Fog base level"),
        ("oct_view_cam.post_processing.fog_half_density_height",                     "Postprocess: Fog half density height"),
        ("oct_view_cam.post_processing.fog_env_contribution",                        "Postprocess: Fog environment contribution"),
        ("oct_view_cam.post_processing.base_fog_color",                              "Postprocess: Base fog color"),
        ("oct_view_cam.post_processing.medium_radius",                               "Postprocess: Medium radius"),

    ]

}