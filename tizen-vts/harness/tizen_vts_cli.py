import argparse
import os
import stat # Required for checking execute permissions more robustly
import subprocess # For executing SDB commands
import xml.etree.ElementTree as ET # For parsing GTest XML
import datetime # For report timestamps

# Default directory where compiled test executables are expected to be found,
# relative to the location of this script.
DEFAULT_TEST_BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "build", "bin")

# Default remote directory on Tizen device for VTS tests
DEFAULT_REMOTE_TEST_DIR = "/opt/usr/devicetests/vts/"
# Subdirectory for results on the remote device
DEFAULT_REMOTE_RESULTS_DIR = os.path.join(DEFAULT_REMOTE_TEST_DIR, "results")
# Default directory on the host machine to store fetched results and reports
DEFAULT_HOST_RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


# SDB executable path (can be overridden by --sdb-path argument)
SDB_EXECUTABLE = "sdb"

def discover_tests(test_dir):
    """
    Discovers executable files in the specified directory.
    These are assumed to be compiled GTest executables.
    """
    if not os.path.isdir(test_dir):
        print(f"Error: Test directory '{test_dir}' not found.")
        return []

    test_executables = []
    for item in os.listdir(test_dir):
        item_path = os.path.join(test_dir, item)
        # Check if it's a file and if it's executable by the owner
        if os.path.isfile(item_path):
            mode = os.stat(item_path).st_mode
            if mode & stat.S_IXUSR: # Check for owner execute permission
                 test_executables.append(item)
    return test_executables

def list_tests_action(args):
    """
    Action to list discovered test executables.
    """
    print(f"Scanning for tests in: {os.path.abspath(args.test_dir)}...")
    tests = discover_tests(args.test_dir)
    if tests:
        print("Available tests:")
        for test_name in tests:
            print(f"  - {test_name}")
    else:
        print("No tests found. Ensure tests are compiled and present in the specified directory.")

def run_test_action(args):
    """
    Action to run a specified test.
    Action to run a specified test.
    This involves:
    1. Constructing the full path to the local test executable.
    2. Pushing it to the Tizen device using SDB.
    3. Executing it on the device via SDB shell.
    4. Fetching XML results from the device.
    5. Parsing the XML results.
    6. Generating a basic HTML report.
    """
    local_test_path = os.path.join(args.test_dir, args.test_name)

    print(f"Attempting to run test: {args.test_name}")
    print(f"  Local path: {os.path.abspath(local_test_path)}")

    if not os.path.isfile(local_test_path):
        print(f"Error: Test executable '{args.test_name}' not found in '{os.path.abspath(args.test_dir)}'.")
        return

    mode = os.stat(local_test_path).st_mode
    if not (mode & stat.S_IXUSR):
        print(f"Error: Test '{args.test_name}' at '{local_test_path}' is not executable.")
        return

    # Ensure host results directory exists
    if not os.path.exists(DEFAULT_HOST_RESULTS_DIR):
        try:
            os.makedirs(DEFAULT_HOST_RESULTS_DIR)
            print(f"Created host results directory: {DEFAULT_HOST_RESULTS_DIR}")
        except OSError as e:
            print(f"Error creating host results directory '{DEFAULT_HOST_RESULTS_DIR}': {e}")
            return


    remote_test_executable_path = os.path.join(DEFAULT_REMOTE_TEST_DIR, "bin", args.test_name) # Store tests in a 'bin' subdirectory on remote
    # DEFAULT_REMOTE_RESULTS_DIR is now a global constant

    try:
        print(f"Pushing '{local_test_path}' to '{remote_test_executable_path}' on device...")
        push_file_to_device(local_test_path, remote_test_executable_path, args)

        print(f"Running '{remote_test_executable_path}' on device...")
        # The XML filename on the device will be based on the test name
        remote_xml_filename = f"{os.path.splitext(args.test_name)[0]}_results.xml"
        run_test_on_device(remote_test_executable_path, DEFAULT_REMOTE_RESULTS_DIR, remote_xml_filename, args)

        print(f"Test '{args.test_name}' execution completed on device.")

        # Fetch results
        remote_xml_filepath = os.path.join(DEFAULT_REMOTE_RESULTS_DIR, remote_xml_filename)
        local_xml_filepath = os.path.join(DEFAULT_HOST_RESULTS_DIR, remote_xml_filename)

        print(f"Fetching results from '{remote_xml_filepath}' to '{local_xml_filepath}'...")
        if fetch_file_from_device(remote_xml_filepath, local_xml_filepath, args):
            print(f"Results XML fetched successfully to {local_xml_filepath}")
            
            parsed_data = parse_gtest_xml(local_xml_filepath)
            if parsed_data:
                report_base_filename = f"{os.path.splitext(args.test_name)[0]}_report"
                report_timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                report_filename = f"{report_base_filename}_{report_timestamp}.html"
                report_filepath = os.path.join(DEFAULT_HOST_RESULTS_DIR, report_filename)
                
                generate_html_report(parsed_data, report_filepath)
                print(f"HTML Test Report generated at: {os.path.abspath(report_filepath)}")
            else:
                print("Failed to parse GTest XML results.")
        else:
            print(f"Failed to fetch test results XML from '{remote_xml_filepath}'.")

    except RuntimeError as e:
        print(f"Error during SDB operation or test execution: {e}")
        print("Please ensure the Tizen device is connected, authorized, and SDB is correctly configured.")
        print("You can specify the SDB path using --sdb-path and target ID using --target-id.")
    except FileNotFoundError: # Specifically for SDB executable not found
        print(f"Error: SDB executable ('{args.sdb_path or SDB_EXECUTABLE}') not found. Is it in your PATH or specified correctly via --sdb-path?")


def execute_sdb_command(sdb_cmd_list, args, check=True):
    """
    Executes an SDB command using subprocess.

    Args:
        sdb_cmd_list (list): The SDB command and its arguments as a list of strings.
                             The first element should be the SDB executable.
        args: Parsed command-line arguments, used to access sdb_path and target_id.
        check (bool): If True, raises RuntimeError if the command fails.

    Returns:
        subprocess.CompletedProcess: The result of the command execution.

    Raises:
        RuntimeError: If the SDB command returns a non-zero exit code and check is True.
        FileNotFoundError: If the SDB executable is not found.
    """
    effective_sdb_executable = args.sdb_path or SDB_EXECUTABLE
    
    # Base command
    full_cmd = [effective_sdb_executable]

    # Add target ID if specified
    if args.target_id:
        full_cmd.extend(["-s", args.target_id])
    
    # Add the rest of the SDB command (already includes sdb_executable placeholder)
    full_cmd.extend(sdb_cmd_list[1:])


    # TODO: Add verbose printing if args.verbose: print(f"Executing SDB command: {' '.join(full_cmd)}")
    try:
        process = subprocess.run(full_cmd, capture_output=True, text=True, check=False) # check=False to handle manually
        if check and process.returncode != 0:
            error_message = (
                f"SDB command failed with exit code {process.returncode}.\n"
                f"Command: {' '.join(full_cmd)}\n"
                f"Stdout: {process.stdout.strip()}\n"
                f"Stderr: {process.stderr.strip()}"
            )
            raise RuntimeError(error_message)
        return process
    except FileNotFoundError:
        # This exception is raised if SDB_EXECUTABLE itself is not found
        raise FileNotFoundError(f"SDB executable not found at '{effective_sdb_executable}'. "
                                "Please ensure it's in your PATH or specify it with --sdb-path.")


def push_file_to_device(local_path, remote_path, args):
    """
    Pushes a file from the host to the Tizen device using SDB.
    Creates the remote directory if it doesn't exist.

    Args:
        local_path (str): Path to the local file.
        remote_path (str): Full path to the destination on the device.
        args: Parsed command-line arguments.
    """
    remote_dir = os.path.dirname(remote_path)
    
    # Create remote directory
    # SDB shell mkdir behavior: if path is /opt/usr/foo/bar, then /opt/usr/foo must exist.
    # `mkdir -p` handles creation of parent directories.
    mkdir_cmd = [SDB_EXECUTABLE, "shell", f"mkdir -p {remote_dir}"]
    print(f"  Creating remote directory (if needed): {remote_dir}")
    execute_sdb_command(mkdir_cmd, args) # Let it raise error if fails

    # Push the file
    push_cmd = [SDB_EXECUTABLE, "push", local_path, remote_path]
    print(f"  Pushing file: {local_path} -> {remote_path}")
    execute_sdb_command(push_cmd, args)
    print(f"  File '{os.path.basename(local_path)}' pushed successfully to '{remote_path}'.")


def run_test_on_device(remote_test_executable_path, remote_results_dir, args):
    """
    Runs a GTest executable on the Tizen device via SDB.

    Args:
        remote_test_executable_path (str): Full path to the test executable on the device.
        target_remote_results_dir (str): Directory on the device to store GTest XML results.
        target_xml_filename (str): The filename for the XML output on the device.
        args: Parsed command-line arguments.
    """
    xml_output_path = f"{target_remote_results_dir}/{target_xml_filename}"

    # Ensure results directory exists on device
    mkdir_cmd = [SDB_EXECUTABLE, "shell", f"mkdir -p {target_remote_results_dir}"]
    print(f"  Creating remote results directory (if needed): {target_remote_results_dir}")
    execute_sdb_command(mkdir_cmd, args)

    # Make the test executable on the device
    chmod_cmd = [SDB_EXECUTABLE, "shell", f"chmod +x {remote_test_executable_path}"]
    print(f"  Making test executable on device: {remote_test_executable_path}")
    execute_sdb_command(chmod_cmd, args)

    # Construct and run the test command
    # Note: Ensure device paths are quoted if they can contain spaces.
    # Using the specific filename for XML output.
    test_cmd_on_device = f"{remote_test_executable_path} --gtest_output=xml:{xml_output_path}"
    sdb_shell_cmd = [SDB_EXECUTABLE, "shell", test_cmd_on_device]

    print(f"  Executing test on device: {test_cmd_on_device}")
    result = execute_sdb_command(sdb_shell_cmd, args, check=False) # Don't check, GTest returns non-zero for failures

    print("--- Device Test Output ---")
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(f"Stderr from device:\n{result.stderr.strip()}")
    print("--- End Device Test Output ---")

    if result.returncode != 0:
        print(f"Warning: Test executable '{os.path.basename(remote_test_executable_path)}' exited with code {result.returncode}. This might indicate test failures. Check XML report.")
    else:
        print(f"Test executable '{os.path.basename(remote_test_executable_path)}' completed on device.")
    # Note: Actual test pass/fail status is in the XML. This print just checks execution.


def fetch_file_from_device(remote_path, local_path, args):
    """
    Fetches a file from the Tizen device to the host using SDB.

    Args:
        remote_path (str): Full path to the file on the device.
        local_path (str): Full path to the destination on the host.
        args: Parsed command-line arguments.

    Returns:
        bool: True if fetch was successful, False otherwise.
    """
    local_dir = os.path.dirname(local_path)
    if not os.path.exists(local_dir):
        try:
            os.makedirs(local_dir)
            print(f"  Created local directory for results: {local_dir}")
        except OSError as e:
            print(f"  Error creating local directory '{local_dir}': {e}")
            return False

    pull_cmd = [SDB_EXECUTABLE, "pull", remote_path, local_path]
    print(f"  Fetching file: {remote_path} -> {local_path}")
    try:
        execute_sdb_command(pull_cmd, args) # Let it raise error if fails
        print(f"  File '{os.path.basename(remote_path)}' fetched successfully.")
        return True
    except RuntimeError as e:
        print(f"  Error fetching file: {e}")
        # Check if the error is because the file doesn't exist on remote
        if "No such file or directory" in str(e) or "file does not exist" in str(e).lower():
             print(f"  Hint: The file '{remote_path}' may not exist on the device. Was the test run correctly and did it produce output?")
        return False
    except FileNotFoundError: # SDB not found
        print(f"Error: SDB executable ('{args.sdb_path or SDB_EXECUTABLE}') not found.")
        return False


def parse_gtest_xml(xml_file_path):
    """
    Parses a GTest XML results file.
    """
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot() # Should be <testsuites> or <testsuite>
    except FileNotFoundError:
        print(f"Error: XML results file not found at '{xml_file_path}'.")
        return None
    except ET.ParseError as e:
        print(f"Error: Failed to parse XML file '{xml_file_path}': {e}")
        return None

    parsed_data = {"testsuites": [], "overall": {}}
    overall_summary = {"tests": 0, "failures": 0, "disabled": 0, "errors": 0, "time": 0.0}

    # GTest XML can have a single <testsuites> root or multiple <testsuite> roots (less common)
    # Or sometimes a single <testsuite> as the root if only one suite ran.
    
    # Handle cases where root is <testsuites> (plural)
    source_elements = root.findall('testsuite')
    if not source_elements and root.tag == 'testsuite': # Root is a single <testsuite>
        source_elements = [root]
    elif not source_elements and root.tag != 'testsuites': # Unexpected root
         print(f"Warning: Unexpected root tag '{root.tag}' in XML. Expected 'testsuites' or 'testsuite'.")
         return None


    for suite_element in source_elements:
        suite_data = {
            "name": suite_element.get("name", "UnknownSuite"),
            "tests": suite_element.get("tests", "0"),
            "failures": suite_element.get("failures", "0"),
            "disabled": suite_element.get("disabled", "0"),
            "errors": suite_element.get("errors", "0"),
            "time": suite_element.get("time", "0.0"),
            "testcases": []
        }
        try:
            overall_summary["tests"] += int(suite_data["tests"])
            overall_summary["failures"] += int(suite_data["failures"])
            overall_summary["disabled"] += int(suite_data["disabled"])
            overall_summary["errors"] += int(suite_data["errors"])
            overall_summary["time"] += float(suite_data["time"])
        except ValueError:
            print(f"Warning: Non-integer value for test counts/failures in suite '{suite_data['name']}'.")


        for case_element in suite_element.findall("testcase"):
            case_data = {
                "name": case_element.get("name", "UnknownCase"),
                "status": case_element.get("status", "unknown"), # e.g. "run", "notrun"
                "result": case_element.get("result", "unknown"), # e.g. "completed" (can be inferred)
                "time": case_element.get("time", "0.0"),
                "failure": None
            }
            failure_element = case_element.find("failure")
            if failure_element is not None:
                case_data["result"] = "failed" # Infer result
                case_data["failure"] = {
                    "message": failure_element.get("message", "No message"),
                    "type": failure_element.get("type", "") # Often not present, but good to capture
                }
                # Sometimes failure message is in text content
                if failure_element.text and failure_element.text.strip():
                    case_data["failure"]["message"] = failure_element.text.strip()

            elif case_data["status"] == "run": # If it ran and no failure tag, assume passed
                 case_data["result"] = "passed"
            
            # GTest also has <skipped> for disabled tests, but this is usually at suite level by 'disabled' count
            # If a testcase has status="notrun" and its name is in a --gtest_filter=-..., it's disabled.
            if case_data["status"] == "notrun" : # Could be due to filter or being disabled
                # Heuristic: if suite disabled count > 0 and this is notrun, could be disabled.
                # For simplicity, just mark as skipped if not run.
                 case_data["result"] = "skipped"


            suite_data["testcases"].append(case_data)
        parsed_data["testsuites"].append(suite_data)

    parsed_data["overall"] = {k: str(v) for k, v in overall_summary.items()}
    parsed_data["overall"]["time"] = f"{overall_summary['time']:.3f}" # Format time

    return parsed_data


def generate_html_report(parsed_results, report_file_path):
    """
    Generates a basic HTML report from parsed GTest XML results.
    """
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Tizen VTS Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .summary-table th { background-color: #e0e0e0; }
        .failed { background-color: #ffcccc; }
        .passed { background-color: #ccffcc; }
        .skipped { background-color: #ffffcc; }
        .details { white-space: pre-wrap; font-family: monospace; }
        .timestamp { font-size: 0.9em; color: #555; margin-bottom:20px; }
    </style>
</head>
<body>
    <h1>Tizen VTS Test Report</h1>
"""
    html_content += f"<div class='timestamp'>Report generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>\n"

    # Overall Summary
    overall = parsed_results.get("overall", {})
    html_content += "<h2>Overall Summary</h2>\n"
    html_content += "<table class='summary-table'>\n<tr>"
    headers = ["Total Tests", "Failures", "Disabled", "Errors", "Time (s)"]
    keys = ["tests", "failures", "disabled", "errors", "time"]
    for header, key in zip(headers, keys):
        html_content += f"<th>{header}</th><td>{overall.get(key, 'N/A')}</td>"
    html_content += "</tr>\n</table>\n"

    # Per-Suite Details
    for suite in parsed_results.get("testsuites", []):
        html_content += f"<h2>Test Suite: {suite.get('name', 'Unnamed Suite')}</h2>\n"
        html_content += "<p>"
        html_content += f"Tests: {suite.get('tests', '0')}, "
        html_content += f"Failures: {suite.get('failures', '0')}, "
        html_content += f"Disabled: {suite.get('disabled', '0')}, "
        html_content += f"Errors: {suite.get('errors', '0')}, "
        html_content += f"Time: {suite.get('time', '0.0')}s"
        html_content += "</p>\n"

        html_content += "<table>\n<tr><th>Name</th><th>Status</th><th>Result</th><th>Time (s)</th><th>Failure Details</th></tr>\n"
        for case in suite.get("testcases", []):
            result_class = case.get('result', 'unknown')
            html_content += f"<tr class='{result_class}'>\n"
            html_content += f"<td>{case.get('name', 'N/A')}</td>\n"
            html_content += f"<td>{case.get('status', 'N/A')}</td>\n"
            html_content += f"<td>{result_class}</td>\n"
            html_content += f"<td>{case.get('time', 'N/A')}</td>\n"
            failure_info = case.get('failure')
            if failure_info:
                msg = failure_info.get('message', 'No details').replace('<', '&lt;').replace('>', '&gt;')
                # type_info = f"Type: {failure_info.get('type', 'N/A')}<br>" if failure_info.get('type') else ""
                html_content += f"<td class='details'>{msg}</td>\n"
            else:
                html_content += "<td>N/A</td>\n"
            html_content += "</tr>\n"
        html_content += "</table>\n"

    html_content += "</body>\n</html>"

    try:
        with open(report_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"  HTML report written to {report_file_path}")
    except IOError as e:
        print(f"Error writing HTML report to '{report_file_path}': {e}")


def main():
    """
    Main function to parse arguments and dispatch actions.
    """
    parser = argparse.ArgumentParser(
        description="Tizen Vendor Test Suite (VTS) CLI Harness. "\
                    "Manages deployment and execution of tests on Tizen devices, and processes results.",
        formatter_class=argparse.RawTextHelpFormatter # To allow newlines in help
    )
    parser.add_argument(
        "--test-dir",
        default=DEFAULT_TEST_BUILD_DIR,
        help=f"Directory containing compiled local test executables.\n(default: {DEFAULT_TEST_BUILD_DIR})"
    )
    parser.add_argument(
        "--sdb-path",
        default=None, 
        help=f"Path to the SDB executable.\n(default: '{SDB_EXECUTABLE}' from PATH if not specified)"
    )
    parser.add_argument(
        "-s", "--target-id",
        default=None,
        help="Target Tizen device ID (serial number or emulator ID, e.g., emulator-26101)\nif multiple devices/emulators are connected."
    )
    parser.add_argument(
        "--host-results-dir",
        default=DEFAULT_HOST_RESULTS_DIR,
        help=f"Directory on the host to store fetched XML results and HTML reports.\n(default: {DEFAULT_HOST_RESULTS_DIR})"
    )
    parser.add_argument(
        "--remote-test-root",
        default=DEFAULT_REMOTE_TEST_DIR,
        help=f"Root directory on the Tizen device for VTS tests and results.\n(default: {DEFAULT_REMOTE_TEST_DIR})"
    )
    # TODO: Add --verbose flag and integrate its usage in execute_sdb_command

    subparsers = parser.add_subparsers(dest="command", title="Available commands", 
                                     help="Command to execute. Use '<command> --help' for more details.")
    subparsers.required = True

    # Subparser for the 'list_tests' command
    list_parser = subparsers.add_parser("list_tests", 
                                      help="List all available local test executables from the --test-dir.")
    list_parser.set_defaults(func=list_tests_action)

    # Subparser for the 'run_test' command
    run_parser = subparsers.add_parser("run_test", help="Run a specific test executable on a Tizen device.")
    run_parser.add_argument("test_name", help="Name of the test executable to run (must be present in --test-dir).")
    run_parser.set_defaults(func=run_test_action)

    args = parser.parse_args()
    
    # Update SDB_EXECUTABLE if --sdb-path is provided
    # This is handled within execute_sdb_command now by checking args.sdb_path
    # if args.sdb_path:
    #     global SDB_EXECUTABLE
    #     SDB_EXECUTABLE = args.sdb_path

    args.func(args)

if __name__ == "__main__":
    main()
