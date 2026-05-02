import traceback
import requests
import json
import sys
import re

def print_colored(text: str, color: str) -> None:
    """Prints colored text."""
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m",
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    print(f"{color_code}{text}\033[0m")


def input_colored(prompt: str, color: str) -> str:
    """Gets user input with a colored prompt."""
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m",
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    return input(f"{color_code}{prompt}\033[0m")


def get_channels(_url: str, timeout: int = 10) -> str:
    try:
        #print_colored(f"url: {_url}", "yellow")
        response = requests.get(_url, timeout=timeout)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            return data
        
            #return (data['name'], data['groups'][0]['channels'])            
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        print_colored(f"Error get channels: {e}", "red")
        
        if "response" in locals() and response and response.status_code != 403:
            print_colored(f"Server response: {response.status_code}, text: {response.text}", "yellow")
        return None
    except Exception as ex:
        print_colored(f"Error fetching token: Exception: {ex}", "red")
        if "response" in locals() and response and response.status_code != 403:
            print_colored(f"Server response: {response.text}", "yellow")
        return None


def save_channels_list(channels_data: str, file_name: str, update_channel_name: bool = False) -> None:
    group_name = channels_data['name']
    group_logo = channels_data['image']['url']
    channels = channels_data['groups'][0]['channels']
    count = 0
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")
            for channel in channels:
                channel_id = channel.get("id", "")
                channel_logo = channel["image"].get("url", "")
                #print_colored(f'channel: {channel}', "yellow")
                for source in channel["sources"]:
                    #print_colored(f'    source: {source}', "yellow")
                    for content in source["contents"]:
                        #print_colored(f'        content: {content}', "yellow")
                        for stream in content["streams"]:
                            #print_colored(f'            stream: {stream}', "yellow")
                            stream_links = stream["stream_links"]
                            for stream_link in stream_links:
                                #print_colored(f'                stream_link: {stream_link}', "yellow")
                                request_headers = stream_link.get("request_headers", None)
                                channel_url = stream_link.get("url", "#https://localhost")
                                #print_colored(f'stream_link: {channel_url}', "yellow")
                                ch_name = channel.get("name", "Unknown Channel")
                                
                                # swap name and time of the match
                                if update_channel_name and " | " in ch_name:  
                                    names = ch_name.split(" | ")
                                    ch_name = f'{names[1]} | {names[0]}'
                                
                                channel_name = f'{ch_name} ({stream_link.get("name", "")}) [{stream_link.get("type", "")}]'
                                #print_colored(f'channel_name: {channel_name}', "yellow")
                            
                                if count <= 1:
                                    file.write(
                                        f'#EXTINF:-1 tvg-logo="{channel_logo}" group-title="{group_name}" group-logo="{group_logo}" , {channel_name}\n'
                                    )
                                else:
                                    file.write(
                                        f'#EXTINF:-1 tvg-logo="{channel_logo}" group-title="{group_name}" , {channel_name} \n'
                                    )
                                if request_headers:
                                    file.write(f'#EXTVLCOPT:http-referrer={request_headers[0]["value"]}\n')
                                    file.write(f'#EXTVLCOPT:http-user-agent={request_headers[1]["value"]}\n')
                        
                                file.write(f"{channel_url}\n\n")
                                
                                count += 1
                                
        print_colored(f"\nTotal channels found: {count}", "green")
        print_colored(f"Channel list saved to: {file_name}", "blue")
    except IOError as e:
        print_colored(f"Error saving channel list file: {e}", "red")


def main() -> None:
    """Main function to orchestrate the process."""
    try:
        print_colored(f"Starting the process...", "blue")
        if len(sys.argv) >= 3:
            channels_data = get_channels(sys.argv[1])
            #print_colored(f"response = {channels_data['name']} ; {channels_data['image']['url']}", "yellow")
            #print_colored(f"channels = {channels_data['groups'][0]['channels']}", "yellow")
            if (len(sys.argv) == 4):
                save_channels_list(channels_data, sys.argv[2], sys.argv[3] == "1")
            else:
                save_channels_list(channels_data, sys.argv[2])
        else:
            #channels_data = get_channels("https://tinyurl.com/buncha2")
            #save_channels_list(channels_data, "buncha.m3u", True)
            
            print_colored(f"USE: python json2m3u.py  <link_to_json_file>  <file_name.m3u> <swap_name_and_time: 0 (default) or 1>", "blue")
        
    except KeyboardInterrupt:
        print_colored("\nExiting gracefully...", "yellow")
    except Exception as e:
        # error_str = traceback.format_exc()
        print_colored(f"An unexpected error occurred in main: {e}", "red")
        # print_colored(f"An unexpected error occurred in main: {error_str}", "red")
        
    sys.exit(0)
if __name__ == "__main__":
    main()
