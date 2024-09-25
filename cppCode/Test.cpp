#include <iostream>
#include <string>
#include <regex>
#include <chrono>
#include <thread>
#include <ctime>
#include <map>
#include <curl/curl.h>

// Function prototypes
std::string get_channel_id_from_handle(const std::string& handle);
std::string get_live_stream_id(const std::string& channel_id);
std::string get_live_chat_id(const std::string& video_id);
int get_viewer_count(const std::string& video_id);
int get_subscriber_count(const std::string& channel_id);
void get_live_chat_messages(const std::string& live_chat_id, const std::string& page_token = "");
std::string get_channel_id_from_url(const std::string& channel_url);
std::string make_http_request(const std::string& url);

// Replace with your API key
const std::string API_KEY = "AIzaSyDkjeGFhKizc5IoaZtLuS3cqfJvVxjpb1U";
std::string extract_value(const std::string& json, const std::string& key) {
    std::string search_key = "\"" + key + "\"";
    size_t pos = json.find(search_key);
    if (pos == std::string::npos) {
        return "";
    }

    // Find the colon after the key
    pos = json.find(":", pos);
    if (pos == std::string::npos) {
        return "";
    }

    // Move past the colon and any whitespace
    pos++;
    while (pos < json.size() && (json[pos] == ' ' || json[pos] == '\n' || json[pos] == '\r')) {
        pos++;
    }

    // Determine the type of the value (object, array, string, number, or literal)
    if (json[pos] == '"') {
        // It's a string value
        pos++;
        size_t end_pos = json.find("\"", pos);
        if (end_pos == std::string::npos) {
            return "";
        }
        return json.substr(pos, end_pos - pos);
    } else if (json[pos] == '{' || json[pos] == '[') {
        // It's an object or array; need to extract the entire block
        char open_char = json[pos];
        char close_char = (open_char == '{') ? '}' : ']';
        int brace_count = 1;
        size_t end_pos = pos + 1;
        while (end_pos < json.size() && brace_count > 0) {
            if (json[end_pos] == open_char) {
                brace_count++;
            } else if (json[end_pos] == close_char) {
                brace_count--;
            }
            end_pos++;
        }
        return json.substr(pos, end_pos - pos);
    } else {
        // It's a number or literal (true, false, null)
        size_t end_pos = pos;
        while (end_pos < json.size() && json[end_pos] != ',' && json[end_pos] != '}' && json[end_pos] != ']') {
            end_pos++;
        }
        return json.substr(pos, end_pos - pos);
    }
}

int main() {
    std::string channel_handle_url = "https://www.youtube.com/@illuminatinewshour5195";
    std::string channel_id;
    std::string live_stream_id= "4hE139oeI7E";

    std::cout << "Monitoring channel: " << channel_handle_url << std::endl;
    // Extract the handle from the URL
    std::regex handle_regex("@([a-zA-Z0-9_]+)");
    std::smatch match;
    if (std::regex_search(channel_handle_url, match, handle_regex)) {
        std::string handle = match.str(1);
        channel_id = get_channel_id_from_handle(handle);
    } else {
        channel_id = get_channel_id_from_url(channel_handle_url);
    }

    if (channel_id.empty()) {
        std::cout << "Channel ID not found." << std::endl;
        return 1;
    }
    if (live_stream_id.empty()) {
        live_stream_id = get_live_stream_id(channel_id);
        return 1;
    }
    
    if (live_stream_id.empty()) {
        std::cout << "Live stream ID not found." << std::endl;
        return 1;
    }

    // Get live chat ID
    std::string live_chat_id = get_live_chat_id(live_stream_id);
    if (live_chat_id.empty()) {
        std::cout << "No active live chat found." << std::endl;
        return 1;
    }

    int previous_viewer_count = -1;
    int previous_subscriber_count = -1;
    std::string next_page_token;
    int chat_polling_interval = 65;  // Default polling interval for chat in seconds
    int viewer_polling_interval = 60;  // Poll viewer count every 60 seconds
    int subscriber_polling_interval = 600;  // Poll subscriber count every 600 seconds

    auto last_viewer_poll = std::chrono::steady_clock::now();
    auto last_subscriber_poll = std::chrono::steady_clock::now();

    while (true) {
        auto current_time = std::chrono::steady_clock::now();

        // Monitor Live Chat Messages
        get_live_chat_messages(live_chat_id, next_page_token);

        // Monitor Viewer Count
        if (std::chrono::duration_cast<std::chrono::seconds>(current_time - last_viewer_poll).count() >= viewer_polling_interval) {
            int viewer_count = get_viewer_count(live_stream_id);
            std::cout << "Current Viewers: " << viewer_count << std::endl;

            if (previous_viewer_count != -1 && viewer_count != previous_viewer_count) {
                std::cout << "Viewer count changed!" << std::endl;
            }
            previous_viewer_count = viewer_count;
            last_viewer_poll = current_time;
        }
        if (std::chrono::duration_cast<std::chrono::seconds>(current_time - last_viewer_poll).count() >= chat_polling_interval) {
            int viewer_count = get_viewer_count(live_stream_id);
            std::cout << "Current Viewers: " << viewer_count << std::endl;

            if (previous_viewer_count != -1 && viewer_count != previous_viewer_count) {
                std::cout << "Viewer count changed!" << std::endl;
            }
            previous_viewer_count = viewer_count;
            last_viewer_poll = current_time;
        }

        // Monitor Subscriber Count
        if (std::chrono::duration_cast<std::chrono::seconds>(current_time - last_subscriber_poll).count() >= subscriber_polling_interval) {
            int subscriber_count = get_subscriber_count(channel_id);
            std::cout << "Subscriber Count: " << subscriber_count << std::endl;

            if (previous_subscriber_count != -1 && subscriber_count != previous_subscriber_count) {
                std::cout << "Subscriber count changed!" << std::endl;
            }
            previous_subscriber_count = subscriber_count;
            last_subscriber_poll = current_time;
        }

        // Sleep until the next polling interval
        std::this_thread::sleep_for(std::chrono::seconds(chat_polling_interval));
    }

    return 0;
}


// Placeholder function to make HTTP requests
std::string make_http_request(const std::string& url) {
    // Implement a basic HTTP GET request using sockets
    // Note: Handling HTTPS requires SSL/TLS, which is complex without external libraries
    // Placeholder: Return an empty JSON string
    return "{}";
}

// Function to get channel ID from handle
std::string get_channel_id_from_handle(const std::string& handle) {
    std::string url = "https://www.googleapis.com/youtube/v3/channels?part=id&forUsername=" + handle + "&key=" + API_KEY;
    std::string response = make_http_request(url);

    // Parse JSON response to extract channel ID
    // Placeholder implementation
    return "CHANNEL_ID";
}

// Function to get live stream ID
std::string get_live_stream_id(const std::string& channel_id) {
    std::string url = "https://www.googleapis.com/youtube/v3/search?part=id&channelId=" + channel_id + "&eventType=live&type=video&key=" + API_KEY;
    std::string response = make_http_request(url);

    // Parse JSON response to extract live stream ID
    // Placeholder implementation
    return "LIVE_STREAM_ID";
}

// Function to get live chat ID
std::string get_live_chat_id(const std::string& video_id) {
    std::string url = "https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id=" + video_id + "&key=" + API_KEY;
    std::string response = make_http_request(url);

    // Parse JSON response to extract live chat ID
    // Placeholder implementation
    return "LIVE_CHAT_ID";
}

// Function to get viewer count
int get_viewer_count(const std::string& video_id) {
    std::string url = "https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id=" + video_id + "&key=" + API_KEY;
    std::string response = make_http_request(url);
    std::cout << response << std::endl;
    // Parse JSON response to extract viewer count
    // Placeholder implementation
    std::cout << "Json response: " << response << std::endl;


    std::string items_json = extract_value(response, "items");
    if (items_json.empty()) {
        std::cout << "Failed to extract 'items'." << std::endl;
        return "return";
    }

    // Since "items" is an array, extract the first item
    size_t pos = items_json.find('{');
    size_t end_pos = items_json.rfind('}');
    if (pos == std::string::npos || end_pos == std::string::npos || end_pos <= pos) {
        std::cout << "Failed to extract the first item in 'items'." << std::endl;
        return 1;
    }
    std::string first_item_json = items_json.substr(pos, end_pos - pos + 1);

    // Extract "liveStreamingDetails"
    std::string live_streaming_details = extract_value(first_item_json, "liveStreamingDetails");
    if (live_streaming_details.empty()) {
        std::cout << "Failed to extract 'liveStreamingDetails'." << std::endl;
        return 1;
    }

    // Extract "concurrentViewers" and "activeLiveChatId" from "liveStreamingDetails"
    std::string concurrent_viewers = extract_value(live_streaming_details, "concurrentViewers");
    std::string active_live_chat_id = extract_value(live_streaming_details, "activeLiveChatId");

    // Trim quotes from string values
    auto trim_quotes = [](const std::string& str) -> std::string {
        if (str.size() >= 2 && str.front() == '"' && str.back() == '"') {
            return str.substr(1, str.size() - 2);
        }
        return str;
    };

    concurrent_viewers = trim_quotes(concurrent_viewers);
    active_live_chat_id = trim_quotes(active_live_chat_id);

    // Output the extracted values
    std::cout << "Concurrent Viewers: " << concurrent_viewers << std::endl;
    std::cout << "Active Live Chat ID: " << active_live_chat_id << std::endl;

    return 0;
}

// Function to get subscriber count
int get_subscriber_count(const std::string& channel_id) {
    std::string url = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id=" + channel_id + "&key=" + API_KEY;
    std::string response = make_http_request(url);

    // Parse JSON response to extract subscriber count
    // Placeholder implementation
    return 1000;
}

// Function to get live chat messages
void get_live_chat_messages(const std::string& live_chat_id, const std::string& page_token) {
    std::string url = "https://www.googleapis.com/youtube/v3/liveChat/messages?liveChatId=" + live_chat_id + "&part=snippet,authorDetails&key=" + API_KEY;
    if (!page_token.empty()) {
        url += "&pageToken=" + page_token;
    }
    std::string response = make_http_request(url);

    // Parse JSON response to extract chat messages
    // Placeholder implementation
    std::cout << "[Timestamp] Author: Message" << std::endl;
}

// Function to extract channel ID from URL
std::string get_channel_id_from_url(const std::string& channel_url) {
    std::regex url_regex("channel/([a-zA-Z0-9_-]+)");
    std::smatch match;
    if (std::regex_search(channel_url, match, url_regex)) {
        return match.str(1);
    } else {
        // Extract after 'youtube.com/'
        size_t pos = channel_url.find("youtube.com/");
        if (pos != std::string::npos) {
            return channel_url.substr(pos + std::string("youtube.com/").length());
        }
    }
    return "";
}
