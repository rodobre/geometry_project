import argparse
import matplotlib.pyplot as plt
import json

def orientation(a,b,c):
	val = b[0] * c[1] - c[0] * b[1] - a[0] * c[1] + c[0] * a[1] + a[0] * b[1] - b[0] * a[1]
	if val >= 0:
		return 1
	else:
		return 0

def area(a, b, c):
	lhs = a[0] * b[1] + b[0] * c[1] + c[0] * a[1]
	rhs = b[1] * c[0] + c[1] * a[0] + a[1] * b[0]
	return 0.5 * abs(lhs - rhs)

def get_angle_points(points, idx):
	points_len = len(points)

	if(points_len < 3):
		return None

	if idx == 0:
		return (points[1], points[-1])
	elif idx == (points_len - 1):
		return (points[-2], points[0])
	else:
		return (points[idx - 1], points[idx + 1])

def leftmost_point(points):
	min_idx = 0
	for i in xrange(1, len(points)):
		if points[i][0] < points[min_idx][0]:
			min_idx = i
		elif points[i][0] == points[min_idx][0]:
			if points[i][1] > points[min_idx][1]:
				min_idx = i
	return min_idx

def determine_principal_points(points):
	angle_points = None
	not_principal = False
	principal_points = []
	nonprincipal_points = []

	for point_idx, point in enumerate(points):
		angle_points = get_angle_points(points, point_idx)
		print('For point {} at idx {} we have angle points {}'.format(point, point_idx, angle_points))
		point_tuple = (angle_points[0], point, angle_points[1])
		current_area = area(angle_points[0], point, angle_points[1])

		not_principal = False
		for other_point_idx, other_point in enumerate(points):
			if other_point == point or other_point == angle_points[0] or other_point == angle_points[1]:
				continue

			print('Taking other point', other_point)

			if current_area == area(angle_points[0], point, other_point) + area(angle_points[0], angle_points[1], other_point) + area(point, angle_points[1], other_point):
				not_principal = True
				nonprincipal_points += [point]
				break

		if not_principal == False:
			principal_points += [point]

	return principal_points, nonprincipal_points

def determine_convexity(points):
	convex_points = []
	concave_points = []

	left_point = leftmost_point(points)
	print(points, left_point)

	new_points = [points[left_point]] + points[left_point+1:] + points[:left_point]
	sign = orientation(new_points[-1],new_points[0],new_points[1])
	for point_idx, point in enumerate(new_points):
		angle_points = get_angle_points(new_points, point_idx)
		if point_idx == 0:
			angle_points = angle_points[::-1]
		print('Point at idx {} is {} and has angle points {}'.format(point_idx, point, angle_points))
		if orientation(angle_points[0], point, angle_points[1]) == sign:
			convex_points += [point]
		else:
			concave_points += [point]
	return (convex_points, concave_points)

def plot_points_by_category(fig, ax, points, category, color):
	x_coords = [point[0] for point in points]
	y_coords = [point[1] for point in points]
	ax.scatter(x_coords, y_coords, c=color, s=100.0, label=category, alpha=1.0, edgecolors='none')

def draw_lines_between_points(plt, points):
	print('Points to work with', points)
	x_coords = [point[0] for point in points] + [points[0][0]]
	y_coords = [point[1] for point in points] + [points[0][1]]
	plt.plot(x_coords, y_coords, color='black', linewidth=2, markersize=12)

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="Process the polygon and determine nature")
	parser.add_argument('inputfile', help="File containing the polyogn as an array of points")
	inputfile = parser.parse_args().inputfile

	content = None
	with open(inputfile, 'r') as file_input:
		content = file_input.read()

	points = json.loads(content)['points']
	formatted_points = []

	for point in points:
		formatted_points += [(point[0], point[1])]

	points = formatted_points
	print('Loaded points array', points)

	print(area((4,0), (7,2), (2,3)))
	principal_points, nonprincipal_points = determine_principal_points(points)
	print('Principal points', principal_points)
	print('Nonprincipal points', nonprincipal_points)

	convex_points, concave_points = determine_convexity(points)
	print('Convex points', convex_points)
	print('Concave points', concave_points)

	principal_convex_points = [point for point in principal_points if point in convex_points]
	principal_concave_points = [point for point in principal_points if point in concave_points]
	nonprincipal_convex_points = [point for point in nonprincipal_points if point in convex_points]
	nonprincipal_concave_points = [point for point in nonprincipal_points if point in concave_points]

	print('Principal convex points', principal_convex_points)
	print('Principal concave points', principal_concave_points)
	print('Non-principal convex poiints', nonprincipal_convex_points)
	print('Non-principal concave points', nonprincipal_concave_points)

	fig, ax = plt.subplots()
	draw_lines_between_points(plt, points)
	plot_points_by_category(fig, ax, principal_convex_points, 'Principal convex', 'tab:green')
	plot_points_by_category(fig, ax, principal_concave_points, 'Principal concave', 'tab:red')
	plot_points_by_category(fig, ax, nonprincipal_convex_points, 'Non-principal convex', 'tab:blue')
	plot_points_by_category(fig, ax, nonprincipal_concave_points, 'Non-principal concave', 'tab:orange')
	ax.legend()
	ax.grid(True)
	plt.show()
