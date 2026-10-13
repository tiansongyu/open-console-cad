"""Reproduce image measurements without distributing Nintendo's images.

Usage: python measure_references.py /path/to/local/reference-cache
Requires numpy, scipy, OpenCV and matplotlib. Downloads only missing references;
requires their recorded SHA-256 hashes so silently changed images are not used.
Patent coordinates refer to a 1400-pixel-high rendering of the PDF (pdftoppm).
These are approximate image measurements, not manufacturing dimensions.
"""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request
import cv2
import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
args = argparse.ArgumentParser(description=__doc__)
args.add_argument('cache', type=Path)
cache = args.parse_args().cache
cache.mkdir(parents=True, exist_ok=True)
sources = [
    {'file': 'body-switch03-front.jpg',
     'url': 'https://www.nintendo.com/sg/hardware/detail/switch/img/08-local-specs/body-switch03-front.jpg',
     'sha256': 'a722de2302f0436accdfab5202763fccfa7992cb3f35eac1c99764c8e214a440',
     'author': 'Nintendo', 'use': 'Retail front view; contour and face-button diameters'},
    {'file': 'USD819642S1.pdf',
     'url': 'https://patentimages.storage.googleapis.com/57/37/2a/8dd4c3079855b2/USD819642S1.pdf',
     'sha256': 'b87297526c12fd3cb73307284293184942d012115ac13b8c3ad660529682e036',
     'author': 'Nintendo Co., Ltd.', 'use': 'Design patent Figures 3 and 4; edge-transition extents'},
]
for source in sources:
    path = cache / source['file']
    if not path.exists():
        urllib.request.urlretrieve(source['url'], path)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256'], path

im = cv2.imread(str(cache / sources[0]['file']))
assert im.shape[:2] == (1400, 1880)
# Remove red callouts and white background. The ROI excludes labels and rail.
roi = im[150:940, 600:846]
mask = ((roi.max(axis=2).astype(int) - roi.min(axis=2).astype(int)) < 40) & (roi.mean(axis=2) < 210)
ys, xs = np.where(mask)
top, bottom = int(ys.min() + 150), int(ys.max() + 150)
px_per_mm = (bottom - top) / 102
points = []
for y in range(782, 912):
    row = im[y, 590:850]
    ok = ((row.max(axis=1).astype(int) - row.min(axis=1).astype(int)) < 40) & (row.mean(axis=1) < 210)
    x = np.where(ok)[0]
    if len(x):
        points.append((float(x[0] + 590), float(y)))
points = np.asarray(points)
fit = least_squares(lambda t: np.hypot(points[:, 0] - t[0], points[:, 1] - t[1]) - t[2],
                    [755, 760, 155])
gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
buttons = []
for key, (x, y, w, h) in {
    'L_up': (690, 480, 83, 65), 'L_left': (642, 535, 70, 67),
    'R_X': (1100, 275, 73, 60), 'R_A': (1150, 330, 70, 65),
}.items():
    circles = cv2.HoughCircles(gray[y:y+h, x:x+w], cv2.HOUGH_GRADIENT, 1, 60,
                              param1=60, param2=20, minRadius=21, maxRadius=30)
    assert circles is not None and len(circles[0]) == 1, key
    cx, cy, radius = [float(v) for v in circles[0][0]]
    buttons.append({'key': key, 'roi_px': [x, y, w, h],
                    'center_px': [cx+x, cy+y], 'radius_px': radius,
                    'diameter_estimate_mm': 2*radius/px_per_mm})

# Coordinates independently read from patent line groups. Image coordinates
# are normalized to a 1400 px page height, not a stated scale on the patent.
patent_scale = 102 / (1120 - 256)
patent = {
    'page_height_px': 1400, 'height_anchor_y_px': [256, 1120],
    'assumed_height_mm': 102, 'mm_per_px': patent_scale,
    'front_outer_x_px': [366.72, 396.86],
    'rear_outer_x_px': [633.31, 684.06],
    'rear_rail_x_px': [403.28, 408.33],
    'front_outer_setback_estimate_mm': (396.86-366.72)*patent_scale,
    'rear_outer_setback_estimate_mm': (684.06-633.31)*patent_scale,
    'rear_rail_setback_estimate_mm': (408.33-403.28)*patent_scale,
    'face_button_diameter_px_approx': 64,
    'face_button_diameter_estimate_mm': 64*patent_scale,
    'coordinate_method': 'Manual line-group selection in Fig.3/4; orthographic assumption; uniform scale to published overall height',
}
report = {
    'date': '2026-10-13', 'model': 'Nintendo Switch HAC-001 / original Joy-Con',
    'sources': sources,
    'official_dimensions_url': 'https://www.nintendo.com/my/hardware/switch/modal/specs/joy-con.html',
    'patent_product_attribution_url': 'https://www.nintendo.com/us/patents/',
    'photo': {'size_px': [1880, 1400], 'overall_height_y_px': [top, bottom],
              'published_height_mm': 102, 'px_per_mm': px_per_mm,
              'lower_outer_corner_fit': {'center_px': fit.x[:2].tolist(),
                  'radius_px': float(fit.x[2]), 'radius_estimate_mm': float(fit.x[2]/px_per_mm),
                  'residual_rms_px': float(np.sqrt(np.mean(fit.fun**2))),
                  'sample_count': len(points), 'method': 'Least-squares circle, thresholded lower-left contour'},
              'buttons': buttons,
              'mean_button_diameter_estimate_mm': float(np.mean([b['diameter_estimate_mm'] for b in buttons]))},
    'patent': patent,
    'study_choices_mm': {'front_outer_setback': 3.5, 'rear_outer_setback': 6.0,
                         'rail_side_setback': .65, 'face_button_diameter': 7.6,
                         'plan_outer_radius_retained': 20.5},
    'limitations': [
        'Image-derived values are estimates. Published nominal height does not establish all other dimensions.',
        'The patent has no manufacturing dimensions, tolerances or assurance that every detail equals retail tooling.',
        'Line selection, shading, resampling and slight nonuniform image scaling dominate uncertainty.',
        'A low fitted-pixel residual is NOT a measured error against a physical console.',
        'Values are deliberately rounded for the study; no submillimetre hardware accuracy is certified.',
        'The main V16 assembly remains the delivered model. The study is not assembly-fit validated.',
    ],
}
(HERE / 'reference-measurements.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
fig, axes = plt.subplots(1, 3, figsize=(14, 4.7), layout='constrained')
blue, orange, dark = '#456787', '#dc793b', '#23313e'
x = (points[:, 0]-fit.x[0])/px_per_mm
y = (points[:, 1]-fit.x[1])/px_per_mm
axes[0].scatter(x, -y, s=10, c=dark, label='Measured photo edge', alpha=.7)
a = np.linspace(np.pi, 1.5*np.pi, 180)
r = fit.x[2]/px_per_mm
axes[0].plot(r*np.cos(a), r*np.sin(a), c=orange, label=f'Circle fit: about {r:.1f} mm')
axes[0].set(aspect='equal', xlabel='Offset from fitted centre (mm)', ylabel='Offset (mm)',
            title='Retail-photo lower corner')
axes[0].legend(loc='upper right', fontsize=8)
labels = ['Front outer', 'Rear outer', 'Rail side']
target = [patent['front_outer_setback_estimate_mm'], patent['rear_outer_setback_estimate_mm'],
          patent['rear_rail_setback_estimate_mm']]
at = np.arange(3)
axes[1].bar(at-.18, [1.8, 3.1, 3.1], width=.34, color=blue, label='V16 (rail: rear)')
axes[1].bar(at+.18, [3.5, 6, .65], width=.34, color=orange, label='Study')
axes[1].scatter(at+.18, target, marker='_', s=180, color=dark, label='Patent-image estimate')
axes[1].set(xticks=at, xticklabels=labels, ylabel='Projected transition width (mm)',
            title='Unequal edge transitions', ylim=(0, 7.6))
axes[1].legend(fontsize=8)
axes[2].bar(['V16', 'Study', 'Retail image', 'Patent image'],
            [6.36, 7.6, report['photo']['mean_button_diameter_estimate_mm'],
             patent['face_button_diameter_estimate_mm']], color=[blue, orange, '#adb7c0', '#c7cfd5'])
axes[2].set(ylabel='Diameter (mm)', title='Round face buttons', ylim=(0, 9.0))
axes[2].tick_params(axis='x', labelrotation=20)
for ax in axes:
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', color='#e4e8ec', linewidth=.5)
    ax.set_axisbelow(True)
fig.suptitle('Switch exterior calibration / public-source estimates', color=dark, fontsize=16)
fig.supxlabel('Nintendo retail image + D819642 Fig.3/4. Image fits are not factory dimensions or physical accuracy tests.', fontsize=9)
fig.savefig(HERE/'measurements.png', dpi=180)
print(json.dumps({'photo_corner_radius_mm': r,
                  'photo_button_diameter_mm': report['photo']['mean_button_diameter_estimate_mm'],
                  'patent_estimates_mm': target}, indent=2))
