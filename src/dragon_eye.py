from __future__ import annotations

import math
import random
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from config import settings


class DragonEye:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.cx = width // 2
        self.cy = height // 2
        self.iris_x = self.cx
        self.iris_y = self.cy
        self.next_blink_at = self._next_blink_time()
        self.blink_started_at: float | None = None
        self.blink_duration: float = 0.0
        self.blink_factor: float = 0.0

        self.idle_mode = "idle"  # idle | glance | scan
        self.idle_scan_angle = 0.0
        self.idle_scan_speed = random.uniform(0.4, 0.9)
        self.idle_next_switch = time.time() + random.uniform(2.0, 5.0)
        self.idle_glance_target_x = self.cx
        self.idle_glance_target_y = self.cy
        self.idle_glance_origin_x = self.cx
        self.idle_glance_origin_y = self.cy
        self.idle_glance_started_at: float | None = None
        self.idle_glance_duration: float = 0.0

        self.pupil_scale = 1.0
        self._pupil_target = 1.0
        self._next_dilation_change = time.time() + 3.0

        self._build_static_layers()

    # ------------------------------------------------------------------ #
    # static layers (built once)                                          #
    # ------------------------------------------------------------------ #

    def _build_static_layers(self) -> None:
        R = settings.eye_radius
        ir = settings.iris_radius

        # --- sclera: white with edge shading, upper-lid shadow, faint capillaries
        yy, xx = np.mgrid[0:self.height, 0:self.width]
        dx = xx - self.cx
        dy = yy - self.cy
        d = np.sqrt(dx * dx + dy * dy) / R
        inside = d <= 1.0
        t = np.clip(d, 0, 1)

        base = 252.0 - 30.0 * t ** 1.8
        # shadow cast by the upper eyelid
        lid_shadow_y = self.cy - R * 0.35
        shade = np.clip((yy - lid_shadow_y) / (0.55 * R), 0.0, 1.0)
        base = base - 22.0 * (1.0 - shade) * inside

        r = np.clip(base * 0.1, 0, 255)
        g = np.clip(base * 0.2, 0, 255)
        b = np.clip(base * 0.1, 0, 255)

        # wet glossy sheen: soft broad specular on the upper-left of the globe
        sheen_x = self.cx - R * 0.30
        sheen_y = self.cy - R * 0.38
        sd = np.sqrt((xx - sheen_x) ** 2 + (yy - sheen_y) ** 2) / (R * 0.75)
        sheen = np.clip(1.0 - sd, 0, 1) ** 2 * inside
        sheen *= 18.0
        r = np.clip(r + sheen, 0, 255)
        g = np.clip(g + sheen, 0, 255)
        b = np.clip(b + sheen * 0.9, 0, 255)

        # blood vessels: smooth branching curves that grow from the outer edge
        # inward, like real conjunctival vasculature. Paths are generated as
        # gently curving splines (supersampled 2x for smoothness), tapered in
        # width and alpha as they travel.
        rng2 = np.random.default_rng(42)
        SS = 2  # supersample factor for smooth vessel strokes
        mask = Image.new("L", (self.width * SS, self.height * SS), 0)
        mdraw = ImageDraw.Draw(mask)

        def catmull_rom(points, samples_per_seg=8):
            """Smooth spline through control points."""
            if len(points) < 3:
                return points
            pts = [points[0]] + list(points) + [points[-1]]
            out = []
            for i in range(1, len(pts) - 2):
                p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
                for j in range(samples_per_seg):
                    tt = j / samples_per_seg
                    tt2, tt3 = tt * tt, tt * tt * tt
                    x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * tt +
                               (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * tt2 +
                               (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * tt3)
                    y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * tt +
                               (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * tt2 +
                               (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * tt3)
                    out.append((x, y))
            out.append(points[-1])
            return out

        def draw_vessel(px_, py_, heading, segs, seg_len, width_px, strength, depth_limit, depth=0):
            """Build a curved vessel path (arc-like), then stroke it as a smooth tapered curve."""
            ctrl = [(px_ * SS, py_ * SS)]
            # each vessel gets a persistent curvature bias so it forms a smooth
            # arc — this is what makes real vessels look curvy, not jagged
            curvature = rng2.choice([-1.0, 1.0]) * rng2.uniform(0.10, 0.30)
            for i in range(int(segs)):
                heading += curvature + rng2.uniform(-0.06, 0.06)
                px_ += math.cos(heading) * seg_len
                py_ += math.sin(heading) * seg_len
                pd = math.hypot(px_ - self.cx, py_ - self.cy) / R
                if pd < depth_limit:
                    break
                ctrl.append((px_ * SS, py_ * SS))
                # branch off partway through
                if depth < 2 and 0 < i < int(segs) - 1 and rng2.uniform() < 0.3:
                    draw_vessel(px_, py_, heading + rng2.choice([-1.0, 1.0]) * rng2.uniform(0.4, 0.8),
                                max(2, int(segs) * 2 // 3), seg_len * 0.8,
                                max(0, width_px - 1), strength * 0.7, depth_limit, depth + 1)

            pts = catmull_rom(ctrl)
            if len(pts) < 2:
                return
            n = len(pts)
            for i in range(n - 1):
                frac = i / n
                # taper width toward zero so tips dissolve instead of stopping
                w = max(1, int(round(width_px * SS * (1.0 - 0.85 * frac))))
                # alpha falls off faster than width so the tip fades out
                a = strength * max(0.05, (1.0 - 0.8 * frac) ** 1.5)
                mdraw.line([pts[i], pts[i + 1]], fill=int(255 * min(1.0, a)), width=w, joint="curve")

        # trunk vessels: start just outside the globe edge, push inward
        for _ in range(9):
            ang = rng2.uniform(0, 2 * math.pi)
            # favor the left/right corners like a real eye
            if rng2.uniform() < 0.6:
                ang = rng2.choice([rng2.uniform(-0.6, 0.6), rng2.uniform(math.pi - 0.6, math.pi + 0.6)])
            start_r = rng2.uniform(1.04, 1.10) * R
            sx = self.cx + math.cos(ang) * start_r
            sy = self.cy + math.sin(ang) * start_r
            draw_vessel(sx, sy, ang + math.pi + rng2.uniform(-0.3, 0.3),
                        rng2.integers(9, 15), R * 0.075,
                        2, rng2.uniform(0.5, 0.8), 0.40)

        # fine vessels: shallower, thinner, more numerous
        for _ in range(24):
            ang = rng2.uniform(0, 2 * math.pi)
            start_r = rng2.uniform(0.95, 1.08) * R
            sx = self.cx + math.cos(ang) * start_r
            sy = self.cy + math.sin(ang) * start_r
            draw_vessel(sx, sy, ang + math.pi + rng2.uniform(-0.5, 0.5),
                        rng2.integers(5, 9), R * 0.06,
                        1, rng2.uniform(0.25, 0.45), 0.58)

        # downsample for anti-aliased translucent vessels, then soften and tint.
        # Deep blood-red: replace color rather than tint — vessels get their own
        # dark red hue mixed over the white, so they stay saturated and visible.
        cap = np.asarray(mask.resize((self.width, self.height), Image.Resampling.LANCZOS), dtype=float) / 255.0
        # a touch of blur so vessel edges are soft, sitting within the tissue
        cap = np.asarray(Image.fromarray((cap * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), dtype=float) / 255.0
        # keep vessels out of the very center of the globe
        cap_dist = np.sqrt((xx - self.cx) ** 2 + (yy - self.cy) ** 2) / R
        cap *= np.clip((cap_dist - 0.38) / 0.15, 0, 1)

        # vessel color: deep blood red
        vessel_r = 255.0
        vessel_g = 215.0
        vessel_b = 0.0
        blend = np.clip(cap * 1.6, 0.0, 0.92)  # cap at 92% so they stay translucent
        r = r * (1.0 - blend) + vessel_r * blend
        g = g * (1.0 - blend) + vessel_g * blend
        b = b * (1.0 - blend) + vessel_b * blend

        alpha = (inside * 255).astype(np.uint8)

        sclera = np.dstack(
            [r.astype(np.uint8), g.astype(np.uint8), b.astype(np.uint8), alpha]
        )
        sclera_full = Image.fromarray(sclera, "RGBA")

        # Split the sclera into two layers so vessels can move with the eye:
        #   - base: shading/sheen only (static, doesn't move)
        #   - vessels: the vascular texture (moves with the iris/globe rotation)
        blend3 = blend[..., None]
        vessel_color = np.dstack(
            [np.full_like(r, vessel_r), np.full_like(g, vessel_g), np.full_like(b, vessel_b)]
        )
        # base = what the sclera looks like without vessels
        base_np = np.asarray(sclera_full).astype(float)
        scl_np = np.asarray(sclera_full).astype(float)
        # remove vessels from base: invert the blend
        # sclera = base*(1-blend) + vessel*blend  =>  base = (sclera - vessel*blend)/(1-blend)
        denom = np.maximum(1.0 - blend, 0.08)
        base_np[..., 0] = (scl_np[..., 0] - vessel_r * blend) / denom
        base_np[..., 1] = (scl_np[..., 1] - vessel_g * blend) / denom
        base_np[..., 2] = (scl_np[..., 2] - vessel_b * blend) / denom
        base_np[..., 3] = alpha
        self._sclera_base = Image.fromarray(np.clip(base_np, 0, 255).astype(np.uint8), "RGBA")

        # vessel layer: alpha = vessel mask, color = blood red
        vessel_arr = np.dstack(
            [np.full_like(r, vessel_r).astype(np.uint8),
             np.full_like(g, vessel_g).astype(np.uint8),
             np.full_like(b, vessel_b).astype(np.uint8),
             np.clip(blend * 255, 0, 255).astype(np.uint8)]
        )
        self._vessel_layer = Image.fromarray(vessel_arr, "RGBA")

        self._sclera_img = sclera_full
        self._sclera_alpha = alpha

        # --- iris texture: radial gradient + fibers + limbal ring + flecks
        size = ir * 2
        iyy, ixx = np.mgrid[0:size, 0:size]
        icx = icy = size / 2.0
        idd = np.sqrt((ixx - icx) ** 2 + (iyy - icy) ** 2) / ir
        theta = np.arctan2(iyy - icy, ixx - icx)

        rng = np.random.default_rng(11)
        fib = np.zeros_like(idd)
        for _ in range(6):
            fib += np.sin(theta * rng.integers(8, 40) + rng.uniform(0, 2 * math.pi)) * rng.uniform(0.4, 1.0)
        fib /= 6.0

        # radial fiber streaks: bright/dark spokes from pupil toward limbus
        fibers = rng.uniform(0, 2 * math.pi, 90)
        fiber_field = np.zeros_like(idd)
        for fa in fibers:
            ang_diff = np.abs((theta - fa + math.pi) % (2 * math.pi) - math.pi)
            fiber_field += np.clip(1.0 - ang_diff * 18.0, 0, 1) * rng.uniform(0.5, 1.0)
        fiber_field = np.clip(fiber_field, 0, 1)

        # collarette ring (inner boundary of the ciliary zone)
        collarette = np.exp(-((idd - 0.42) ** 2) / 0.004)

        inner = np.array([255, 215, 0], dtype=float)
        outer = np.array([0, 100, 50], dtype=float)
        tt = np.clip(idd, 0, 1)[..., None]
        col = inner * (1 - tt) + outer * tt
        col = col + 16.0 * fib[..., None] * (0.3 + 0.7 * tt)
        col = col + fiber_field[..., None] * np.array([14.0, 10.0, 4.0]) * (1.0 - tt * 0.5)
        col = col - collarette[..., None] * 26.0

        ring = np.clip((idd - 0.78) / 0.22, 0, 1)
        ring_noise = 1.0 + 0.25 * np.sin(theta * 9.0) + 0.15 * np.sin(theta * 23.0 + 1.3)
        col = col * (1 - (ring * ring_noise)[..., None] * 0.88)

        iris_alpha = (idd <= 1.0) * 255
        iris_arr = np.dstack(
            [np.clip(col[..., 0], 0, 255).astype(np.uint8),
             np.clip(col[..., 1], 0, 255).astype(np.uint8),
             np.clip(col[..., 2], 0, 255).astype(np.uint8),
             iris_alpha.astype(np.uint8)]
        )
        self._iris_tex = Image.fromarray(iris_arr, "RGBA")

        # amber flecks for texture (sparse, low-contrast so they read as pigment
        # variation, not glitter)
        fleck_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        fdraw = ImageDraw.Draw(fleck_layer)
        fleck_colors = [
            (198, 170, 108, 34),
            (12, 22, 48, 42),
            (150, 185, 225, 26),
        ]
        for _ in range(90):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(0.35, 0.95) * ir
            px = icx + math.cos(a) * rr
            py = icy + math.sin(a) * rr
            rad = rng.uniform(0.5, 1.3)
            shade_f = fleck_colors[int(rng.integers(0, len(fleck_colors)))]
            fdraw.ellipse([px - rad, py - rad, px + rad, py + rad], fill=shade_f)
        self._iris_tex = Image.alpha_composite(self._iris_tex, fleck_layer)

        # --- pupil sprite (soft-edged black disc, crisper margin than before)
        ps = settings.pupil_radius
        psize = ps * 6
        palpha = Image.new("L", (psize, psize), 0)
        pdraw = ImageDraw.Draw(palpha)
        pdraw.ellipse([psize / 2 - ps * 0.15, psize / 2 - ps * 1.8, psize / 2 + ps * 0.15, psize / 2 + ps * 1.8], fill=255)
        self._pupil_alpha = palpha.filter(ImageFilter.GaussianBlur(1))
        self._pupil_base = ps

        # --- specular highlight sprites (window-shaped like real reflections)
        def make_window_highlight(w: int, h: int, alpha_val: int, blur: int) -> Image.Image:
            hsize_w, hsize_h = w * 2, h * 2
            himg = Image.new("RGBA", (hsize_w, hsize_h), (0, 0, 0, 0))
            hdraw = ImageDraw.Draw(himg)
            # rounded-rect "window pane" reflection with a divider mullion
            hdraw.rounded_rectangle(
                [hsize_w // 2 - w // 2, hsize_h // 2 - h // 2,
                 hsize_w // 2 + w // 2, hsize_h // 2 + h // 2],
                radius=max(2, min(w, h) // 6),
                fill=(255, 255, 255, alpha_val),
            )
            hdraw.rectangle(
                [hsize_w // 2 - 1, hsize_h // 2 - h // 2,
                 hsize_w // 2 + 1, hsize_h // 2 + h // 2],
                fill=(0, 0, 0, 0),
            )
            return himg.filter(ImageFilter.GaussianBlur(blur))

        self._hl_main = make_window_highlight(max(10, int(ir * 0.42)), max(16, int(ir * 0.6)), 200, 4)
        self._hl_secondary = make_window_highlight(max(5, int(ir * 0.16)), max(8, int(ir * 0.22)), 85, 3)

        # pre-warp the highlight sprites so reflections curve with the cornea
        def cornea_warp(sprite: Image.Image, strength: float = 0.22) -> Image.Image:
            w, h = sprite.size
            xxg, yyg = np.meshgrid(np.arange(w), np.arange(h))
            cxw, cyw = (w - 1) / 2, (h - 1) / 2
            nx = (xxg - cxw) / cxw
            ny = (yyg - cyw) / cyw
            rr = np.sqrt(nx ** 2 + ny ** 2)
            warp = 1.0 - strength * (rr ** 2)
            src_x = np.clip(cxw + nx * warp * cxw, 0, w - 1).astype(int)
            src_y = np.clip(cyw + ny * warp * cyw, 0, h - 1).astype(int)
            arr_s = np.asarray(sprite)
            out = arr_s[src_y, src_x]
            return Image.fromarray(out, "RGBA")

        self._hl_main = cornea_warp(self._hl_main)
        self._hl_secondary = cornea_warp(self._hl_secondary, strength=0.15)

        # --- wet lower-lid reflection line sprite (drawn dynamically, no sprite needed)

    # ------------------------------------------------------------------ #
    # behaviour                                                           #
    # ------------------------------------------------------------------ #

    def _next_blink_time(self) -> float:
        return time.time() + random.uniform(*settings.blink_interval_s)

    def _switch_idle_mode(self, now: float) -> None:
        modes = ["idle", "glance", "scan"]
        modes.remove(self.idle_mode)
        self.idle_mode = random.choice(modes)
        if self.idle_mode == "scan":
            self.idle_scan_speed = random.uniform(0.4, 0.9)
        self.idle_next_switch = now + random.uniform(2.0, 5.0)

    def _idle_target(self, now: float) -> tuple[int, int]:
        if now >= self.idle_next_switch:
            self._switch_idle_mode(now)

        if self.idle_mode == "scan":
            self.idle_scan_angle += self.idle_scan_speed * 0.025
            if self.idle_scan_angle > math.pi * 2:
                self.idle_scan_angle -= math.pi * 2
            reach = random.uniform(settings.max_pupil_offset * 0.7, settings.max_pupil_offset)
            tx = int(self.cx + math.cos(self.idle_scan_angle) * reach)
            ty = int(self.cy + math.sin(self.idle_scan_angle * 0.7) * reach * 0.6)
            return tx, ty

        if self.idle_mode == "glance":
            if self.idle_glance_started_at is None:
                self.idle_glance_started_at = now
                self.idle_glance_duration = random.uniform(*settings.idle_glance_duration_s)
                self.idle_glance_origin_x = self.iris_x
                self.idle_glance_origin_y = self.iris_y
                angle = random.uniform(0, math.pi * 2)
                reach = random.uniform(25, settings.max_pupil_offset)
                self.idle_glance_target_x = int(self.cx + math.cos(angle) * reach)
                self.idle_glance_target_y = int(self.cy + math.sin(angle) * reach)

            if now - self.idle_glance_started_at >= self.idle_glance_duration:
                self.idle_glance_started_at = None
                self.idle_mode = "idle"
                self.idle_next_switch = now + random.uniform(1.0, 3.0)
                return int(self.idle_glance_origin_x), int(self.idle_glance_origin_y)

            return self.idle_glance_target_x, self.idle_glance_target_y

        return self.cx, self.cy

    def update(self, target_x: int | None, target_y: int | None, now: float) -> None:
        if target_x is not None and target_y is not None:
            # Add organic microsaccades so the eye doesn't look dead when locked on
            if not hasattr(self, "_saccade_target"):
                self._saccade_target = (0, 0)
                self._next_saccade = now
            
            if now > self._next_saccade:
                # Dart within a 15px radius to "examine" the target
                self._saccade_target = (random.randint(-15, 15), random.randint(-15, 15))
                self._next_saccade = now + random.uniform(0.3, 1.8)
                
            tx = max(0, min(self.width, target_x + self._saccade_target[0]))
            ty = max(0, min(self.height, target_y + self._saccade_target[1]))
            self.idle_mode = "idle"
            self.idle_glance_started_at = None
            self.idle_next_switch = now + random.uniform(2.0, 5.0)
        else:
            tx, ty = self._idle_target(now)

        self.iris_x += (tx - self.iris_x) * settings.smoothing
        self.iris_y += (ty - self.iris_y) * settings.smoothing

        # slow pupil dilation drift
        if now >= self._next_dilation_change:
            self._pupil_target = random.uniform(0.86, 1.16)
            self._next_dilation_change = now + random.uniform(2.0, 6.0)
        self.pupil_scale += (self._pupil_target - self.pupil_scale) * 0.03

        if getattr(settings, "blink_enabled", False):
            if self.blink_started_at is None:
                if now >= self.next_blink_at:
                    self.blink_started_at = now
                    self.blink_duration = random.uniform(0.15, 0.35)
            
            if self.blink_started_at is not None:
                elapsed = now - self.blink_started_at
                if elapsed >= self.blink_duration:
                    self.blink_started_at = None
                    self.next_blink_at = self._next_blink_time()
                    self.blink_factor = 0.0
                else:
                    progress = elapsed / self.blink_duration
                    # power curve to make it stay closed a tiny bit longer
                    self.blink_factor = math.sin(progress * math.pi) ** 0.8
        else:
            self.blink_factor = 0.0

    # ------------------------------------------------------------------ #
    # rendering                                                           #
    # ------------------------------------------------------------------ #

    def gaze(self) -> tuple[float, float]:
        """Normalized gaze direction, -1..1 on each axis, based on iris offset.

        The iris physically travels at most max_pupil_offset px, but that full
        deflection means the eye is looking all the way to that side — so the
        normalized vector is what should be mapped onto the camera view.
        """
        gx = (self.iris_x - self.cx) / max(1, settings.max_pupil_offset)
        gy = (self.iris_y - self.cy) / max(1, settings.max_pupil_offset)
        return max(-1.0, min(1.0, gx)), max(-1.0, min(1.0, gy))

    def render(self) -> Image.Image:
        R = settings.eye_radius
        ir = settings.iris_radius

        # iris position clamped inside the eyeball
        dx = self.iris_x - self.cx
        dy = self.iris_y - self.cy
        dist = math.hypot(dx, dy) or 1.0
        max_offset = settings.max_pupil_offset
        scale = min(max_offset / dist, 1.0)
        iris_cx = int(self.cx + dx * scale)
        iris_cy = int(self.cy + dy * scale)

        canvas = self._sclera_base.copy()

        # globe rotation: the whole eyeball (including vessels) rotates slightly
        # in the direction of gaze, and shifts a fraction of the iris offset —
        # like the conjunctiva sliding over the sclera. Always composite the
        # vessel layer so it's present at center gaze too.
        rot_deg = -dx * 0.004
        vessel_shift_x = int(dx * scale * 0.22)
        vessel_shift_y = int(dy * scale * 0.22)
        vessel_layer = self._vessel_layer.transform(
            (self.width, self.height),
            Image.Transform.AFFINE,
            (1.0, 0.0, -vessel_shift_x, 0.0, 1.0, -vessel_shift_y),
            resample=Image.Resampling.BILINEAR,
        )
        if abs(rot_deg) > 0.05:
            vessel_layer = vessel_layer.rotate(rot_deg, center=(self.cx, self.cy),
                                               resample=Image.Resampling.BILINEAR)
        canvas.alpha_composite(vessel_layer)

        # iris layer
        iris_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        iris_layer.paste(self._iris_tex, (iris_cx - ir, iris_cy - ir), self._iris_tex)
        canvas.alpha_composite(iris_layer)

        # pupil (soft edge, slow dilation) — concentric with the iris
        pr = max(4, int(self._pupil_base * self.pupil_scale))
        psize = int(pr * 6)
        p_alpha = self._pupil_alpha.resize((psize, psize), Image.Resampling.NEAREST)
        pupil_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        black = Image.new("RGBA", (psize, psize), (6, 6, 10, 255))
        pupil_layer.paste(black, (iris_cx - psize // 2, iris_cy - psize // 2), p_alpha)
        canvas.alpha_composite(pupil_layer)

        # wet specular highlights, fixed relative to the light (upper-left),
        # softly warped so they read as corneal reflections rather than stickers
        draw = ImageDraw.Draw(canvas)
        hl1_pos = (iris_cx - int(ir * 0.42), iris_cy - int(ir * 0.48))
        hl2_pos = (iris_cx + int(ir * 0.30), iris_cy + int(ir * 0.34))
        hl1 = self._hl_main  # pre-warped at build time
        hl2 = self._hl_secondary
        canvas.alpha_composite(hl1, (hl1_pos[0] - hl1.width // 2,
                                     hl1_pos[1] - hl1.height // 2))
        canvas.alpha_composite(hl2, (hl2_pos[0] - hl2.width // 2,
                                     hl2_pos[1] - hl2.height // 2))

        # wet reflection line along the bottom of the iris (lower waterline shine)
        draw.arc(
            [iris_cx - int(ir * 0.7), iris_cy - int(ir * 0.5),
             iris_cx + int(ir * 0.7), iris_cy + int(ir * 0.9)],
            start=30, end=150, fill=(255, 255, 255, 70), width=3,
        )

        # soften the eyeball outline (living tissue has no crisp stroke)
        eye_bbox = [self.cx - R, self.cy - R, self.cx + R, self.cy + R]
        draw.ellipse(eye_bbox, outline=(96, 74, 66, 110), width=4)

        # clip everything back to the eyeball circle
        arr = np.asarray(canvas).copy()
        arr[..., 3] = np.minimum(arr[..., 3], self._sclera_alpha)
        canvas = Image.fromarray(arr, "RGBA")

        # solid black background outside the eyeball (so projectors/WebView
        # never show transparent as white), and clip vessels that extend
        # beyond the eyeball circle
        out = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        out.paste(canvas, (0, 0), canvas)
        
        if self.blink_factor > 0.0:
            odraw = ImageDraw.Draw(out)
            lid_r = R * 1.5
            top_y_center = self.cy - R - lid_r + (R * 1.1) * self.blink_factor
            odraw.ellipse([self.cx - lid_r, top_y_center - lid_r, self.cx + lid_r, top_y_center + lid_r], fill=(0, 0, 0))
            
            bot_y_center = self.cy + R + lid_r - (R * 0.9) * self.blink_factor
            odraw.ellipse([self.cx - lid_r, bot_y_center - lid_r, self.cx + lid_r, bot_y_center + lid_r], fill=(0, 0, 0))

        return out
