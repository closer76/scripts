### Import necessary modules
from optparse import OptionParser
from collections import deque
import re

## Global variables
current_usage_page = 0
sensor_usage_id_table = { \
    0x0001: 'Sensor Type Collection', \
    0x0031: 'Sensor Type: Environmental: Atomospheric Pressure', \
    0x0073: 'Sensor Type: Motion: Accelermeter 3D', \
    0x0076: 'Sensor Type: Motion: Gyrometer 3D', \
    0x0083: 'Sensor Type: Orientation: Compass 3D', \
    0x0086: 'Sensor Type: Orientation: Inclinometer 3D', \
    0x008A: 'Sensor Type: Orientation: Device Orientation', \
    0x00E1: 'Sensor Type: Other; Custom', \
    0x0201: 'Sensor State', \
    0x0202: 'Sensor Event', \
    0x0304: 'Sensor Property: Minimum_Report_Interval', \
    0x0305: 'Sensor Property: Sensor_Manufacturer', \
    0x0306: 'Sensor Property: Sensor_Model', \
    0x0309: 'Sensor Property: Sensor_Connection_Type', \
    0x030E: 'Sensor Property: Report_Interval', \
    0x0316: 'Sensor Property: Reporting_State', \
    0x0319: 'Sensor Property: Power_State', \
    0x0431: 'Sensor Data: Environmental_Atmospheric_Pressure', \
    0x0451: 'Sensor Data: Motion: State', \
    0x0452: 'Sensor Data: Motion: Acceleration', \
    0x0453: 'Sensor Data: Motion: Acceleration_X_Axis', \
    0x0454: 'Sensor Data: Motion: Acceleration_Y_Axis', \
    0x0455: 'Sensor Data: Motion: Acceleration_Z_Axis', \
    0x0456: 'Sensor Data: Motion: Angular_Velocity', \
    0x0457: 'Sensor Data: Motion: Angular_Velocity_X_Axis', \
    0x0458: 'Sensor Data: Motion: Angular_Velocity_Y_Axis', \
    0x0459: 'Sensor Data: Motion: Angular_Velocity_Z_Axis', \
    0x0471: 'Sensor Data: Orientation: Magnetic_Heading', \
    0x0475: 'Sensor Data: Orientation: Compensated_Magnetic_North', \
    0x047E: 'Sensor Data: Orientation: Tilt', \
    0x047F: 'Sensor Data: Orientation: Tilt_X', \
    0x0480: 'Sensor Data: Orientation: Tilt_Y', \
    0x0481: 'Sensor Data: Orientation: Tilt_Z', \
    0x0483: 'Sensor Data: Orientation: Quaternion', \
    0x0484: 'Sensor Data: Orientation: Magnetic_Flux', \
    0x0485: 'Sensor Data: Orientation: Magnetic_Flux_X_Axis', \
    0x0486: 'Sensor Data: Orientation: Magnetic_Flux_Y_Axis', \
    0x0487: 'Sensor Data: Orientation: Magnetic_Flux_Z_Axis', \
    0x0488: 'Sensor Data: Orientation: (Reserved?)', \
    0x0543: 'Sensor Data: Custom_Value', \
    0x0544: 'Sensor Data: Custom_Value_1', \
    0x0545: 'Sensor Data: Custom_Value_2', \
    0x0546: 'Sensor Data: Custom_Value_3', \
    0x0547: 'Sensor Data: Custom_Value_4', \
    0x0548: 'Sensor Data: Custom_Value_5', \
    0x0549: 'Sensor Data: Custom_Value_6', \
    0x054A: 'Sensor Data: Custom_Value_7', \
    0x054E: 'Sensor Data: Custom_Value_11', \
    0x054F: 'Sensor Data: Custom_Value_12', \
    0x0550: 'Sensor Data: Custom_Value_13', \
    0x0800: 'Sensor State: Unknown', \
    0x0801: 'Sensor State: Ready', \
    0x0802: 'Sensor State: Not_Available', \
    0x0803: 'Sensor State: No_Data', \
    0x0804: 'Sensor State: Initializing', \
    0x0805: 'Sensor State: Access_Denied', \
    0x0806: 'Sensor State: Error', \
    0x0810: 'Sensor Event: Unknown', \
    0x0811: 'Sensor Event: State_Changed', \
    0x0812: 'Sensor Event: Property_Changed', \
    0x0813: 'Sensor Event: Data_Updated', \
    0x0814: 'Sensor Event: Poll_Response', \
    0x0815: 'Sensor Event: Change_Sensitivity', \
    0x0830: 'Sensor Property: Connection Type: PC_Integrated', \
    0x0831: 'Sensor Property: Connection Type: PC_Attached', \
    0x0832: 'Sensor Property: Connection Type: PC_External', \
    0x0840: 'Sensor Property: Reporting State: No_Events', \
    0x0841: 'Sensor Property: Reporting State: All_Events', \
    0x0842: 'Sensor Property: Reporting State: Threshold_Events', \
    0x0843: 'Sensor Property: Reporting State: No_Events_Wake', \
    0x0844: 'Sensor Property: Reporting State: All_Events_Wake', \
    0x0845: 'Sensor Property: Reporting State: Threshold_Events_Wake', \
    0x0850: 'Sensor Property: Power State: Undefined', \
    0x0851: 'Sensor Property: Power State: D0_Full_Power', \
    0x0852: 'Sensor Property: Power State: D1_Low_Power', \
    0x0853: 'Sensor Property: Power State: D2_Standby_With_Wake', \
    0x0854: 'Sensor Property: Power State: D3_Sleep_With_Wake', \
    0x0855: 'Sensor Property: Power State: D4_Power_Off', \
    0x08E0: '', \
    0x08E1: '', \
    0x08E2: '', \
}

sensor_modifier_table = { \
	0x0000: 'None', \
	0x1000: 'Change_Sensitivity_Abs', \
	0x2000: 'Max', \
	0x3000: 'Min', \
	0x4000: 'Accuracy', \
	0x5000: 'Resolution', \
	0x6000: 'Threshold_High', \
	0x7000: 'Threshold_Low', \
	0x8000: 'Calibration_Offset', \
	0x9000: 'Calibration_Multiplier', \
	0xa000: 'Report_Interval', \
	0xb000: 'Frequency_Max', \
	0xc000: 'Period_Max', \
	0xd000: 'Change_Sensitivity_Range_Pct', \
	0xe000: 'Change_Sensitivity_Rel_Pct', \
	0xf000: 'Vendor_Reserved' \
}

## Helper functions

def hex_list(l):
	return ' '.join('{0:02X}'.format(x) for x in l) + ' ' * (16 - 3 * len(l) + 1)

def attribute_flags(flags):
	return ','.join([ \
		'Constant' if flags & 0x01 else 'Data', \
		'Variable' if flags & 0x02 else 'Array', \
		'Relative' if flags & 0x04 else 'Absolute'])

def handle_usage_page(b0, b1):
	global current_usage_page
	current_usage_page = b1

	outstr = hex_list([b0, b1])
	outstr += ('Usage Page - ' + 'Sensor' if b1 == 0x20 else '(Unknown)')
	return outstr

def handle_usage(b0, b1, b2 = None):
	outstr = hex_list([b0, b1, b2] if b2 else [b0, b1])
	idx = ((b2 << 8) + b1) if b2 else b1
	modifier = idx & 0xF000
	idx = idx & ~modifier		# remove modifier from idx

	if current_usage_page != 0x20:
		outstr += 'Usage = 0x{0:04X}'.format(idx)
	else:
		if idx in sensor_usage_id_table and sensor_usage_id_table[idx] != '':
			outstr += ('Usage - ' + sensor_usage_id_table[idx])
		else:
			outstr += 'Usage - 0x{0:04X}'.format(idx)
			if idx not in sensor_usage_id_table:
				sensor_usage_id_table[idx] = ''

	if modifier != 0:
		outstr += ' [MOD: ' + sensor_modifier_table[modifier] + ']'

	return outstr

def handle_collection(b0, b1):
	outstr = hex_list([b0, b1])
	outstr += 'Collection - '
	if b1 == 0x00:
		outstr += 'Physical'
	elif b1 == 0x01:
		outstr += 'Application'
	elif b1 == 0x02:
		outstr += 'Logical'
	elif b1 == 0x04:
		outstr += 'Named Array'
	elif b1 == 0x05:
		outstr += 'Usage Switch'
	else:
		outstr += '(Unknown)'

	return outstr

def handle_report_id(b0, b1):
	outstr = hex_list([b0,b1])
	outstr += 'Report ID = {}'.format(b1)

	return outstr

def handle_report_size(b0, b1):
	outstr = hex_list([b0, b1])
	outstr += 'Report size = {} bits'.format(b1)

	return outstr

def handle_report_count(b0, b1):
	outstr = hex_list([b0, b1])
	outstr += 'Report count = {}'.format(b1)

	return outstr

def handle_usage_bound(spec, list):
	return hex_list(list) + \
		'Usage ' + spec + ' = 0x' + \
		''.join('{:02X}'.format(x) for x in reversed(list[1:]))

def handle_logical_bound(spec, list):
	return hex_list(list) + \
		'Logical ' + spec + ' = 0x' + \
		''.join('{:02X}'.format(x) for x in reversed(list[1:]))

def handle_exponent(b0, b1):
	outstr = hex_list([b0, b1])
	outstr += 'Exponent = {}'.format(b1)
	return outstr

def handle_input(b0, b1):
	outstr = hex_list([b0, b1])
	outstr += ('Input ({})').format(attribute_flags(b1))
	return outstr

def handle_output(b0, b1):
	outstr = hex_list([b0, b1])
	outstr += ('Input ({})').format(attribute_flags(b1))
	return outstr

def handle_feature(b0, b1):
	outstr = hex_list([b0, b1])
	outstr += ('Input ({})').format(attribute_flags(b1))
	return outstr

def handle_usage_page_vendor(b0, b1, b2):
	global current_usage_page
	outstr = hex_list([b0, b1, b2])
	outstr += 'Usage Page - Vendor: 0x{:02X}'.format(b1)
	current_usage_page = (b2 << 8) + b1
	return outstr

def handle_end_collection(b0):
	outstr = hex_list([b0])
	outstr += 'End Collection'
	return outstr


## Main script

### Parse command-line arguments
parser = OptionParser()
parser.add_option( "-f", "--file",
			action="store", type="string", dest="filename");
(options, args) = parser.parse_args()

# print options.filename


### process file
if options.filename:
	try:
		f = open ( options.filename, 'r')
	except IOError as (errno, strerror):
		print "Cannot open file. (ErrInfo:{0}-{1})".format(errno, strerror)
		sys.exit()

	parse_start = False
	q = []
	for line in f:
		tokens = re.split(' |\t', line)
		for tkn in tokens:
			try:
				num = int(tkn,16)
				q.append(num)
			except:
				break

	f.close()

	l = deque(q)
	while 1:
		try:
			n = l.popleft()
		except:
			break

		if n == 0x05:
			print handle_usage_page(n, l.popleft())
		elif n == 0x09:
			print handle_usage(n, l.popleft())
		elif n == 0xA1:
			print handle_collection(n, l.popleft())
		elif n == 0x85:
			print handle_report_id(n, l.popleft())
		elif n == 0x75:
			print handle_report_size(n, l.popleft())
		elif n == 0x95:
			print handle_report_count(n, l.popleft())
		elif n == 0x19:
			print handle_usage_bound('Min', [n, l.popleft()])
		elif n == 0x29:
			print handle_usage_bound('Max', [n, l.popleft()])
		elif n == 0x15:
			print handle_logical_bound('Min', [n, l.popleft()])
		elif n == 0x25:
			print handle_logical_bound('Max', [n, l.popleft()])
		elif n == 0x55:
			print handle_exponent(n, l.popleft())
		elif n == 0x81:
			print handle_input(n, l.popleft())
		elif n == 0x91:
			print handle_output(n, l.popleft())
		elif n == 0xB1:
			print handle_feature(n, l.popleft())
		elif n == 0x0A:
			print handle_usage(n, l.popleft(), l.popleft())
		elif n == 0x1A:
			print handle_usage_bound('Min', [n, l.popleft(), l.popleft()])
		elif n == 0x2A:
			print handle_usage_bound('Max', [n, l.popleft(), l.popleft()])
		elif n == 0x16:
			print handle_logical_bound('Min', [n, l.popleft(), l.popleft()])
		elif n == 0x26:
			print handle_logical_bound('Max', [n, l.popleft(), l.popleft()])
		elif n == 0x17:
			print handle_logical_bound('Min', [n, l.popleft(), l.popleft(), l.popleft(), l.popleft()])
		elif n == 0x27:
			print handle_logical_bound('Max', [n, l.popleft(), l.popleft(), l.popleft(), l.popleft()])
		elif n == 0xC0:
			print handle_end_collection(n)
		elif n == 0x06:
			print handle_usage_page_vendor(n, l.popleft(), l.popleft())
		else:
			print '{0:02X}'.format(n)

## These are used to generate skeleton of sensor_usage_id_table.
## Not used in final program.
#	print 'sensor_usage_id_table = { \\'
#	for k in sorted(sensor_usage_id_table.keys()):
#		print '    0x{0:04X}: \'{1}\', \\'.format(k, sensor_usage_id_table[k])
#	print '}'
