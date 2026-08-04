#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>

struct Input {
    int parking_minutes;
    std::string vehicle_type;
    int import_wh;
    int import_rate_cents_per_kwh;
    int export_wh;
    int export_rate_cents_per_kwh;
    bool vehicle_v2g;
    bool station_v2g;
    bool owner_opt_in;
    int soc_after_export;
    int minimum_departure_soc;
};

struct Result {
    int parking_fee_cents;
    long long import_cost_cents;
    long long export_credit_cents;
    long long net_amount_cents;
};

void validate(const Input& input) {
    if (input.parking_minutes < 0 || input.parking_minutes > 1440) {
        throw std::invalid_argument("invalid parking_minutes");
    }
    if (input.vehicle_type != "ICE_CAR" && input.vehicle_type != "EV_CAR" &&
        input.vehicle_type != "MOTORCYCLE") {
        throw std::invalid_argument("invalid vehicle_type");
    }
    if (input.import_wh < 0 || input.export_wh < 0 ||
        input.import_rate_cents_per_kwh < 0 || input.export_rate_cents_per_kwh < 0) {
        throw std::invalid_argument("negative energy or tariff");
    }
    if (input.soc_after_export < 0 || input.soc_after_export > 100 ||
        input.minimum_departure_soc < 0 || input.minimum_departure_soc > 100) {
        throw std::invalid_argument("invalid state of charge");
    }
    if (input.export_wh > 0 &&
        (input.vehicle_type != "EV_CAR" || !input.vehicle_v2g ||
         !input.station_v2g || !input.owner_opt_in)) {
        throw std::invalid_argument("V2G export not permitted");
    }
    if (input.export_wh > 0 && input.soc_after_export < input.minimum_departure_soc) {
        throw std::invalid_argument("minimum departure SOC violated");
    }
}

int calculate_parking_fee(const Input& input) {
    if (input.parking_minutes <= 15) {
        return 0;
    }

    const int started_hours = (input.parking_minutes + 59) / 60;
    if (input.vehicle_type == "MOTORCYCLE") {
        return std::min(100 + (started_hours - 1) * 75, 1000);
    }
    return std::min(200 + (started_hours - 1) * 150, 2000);
}

long long calculate_energy_amount(int energy_wh, int rate_cents_per_kwh) {
    const long long product = static_cast<long long>(energy_wh) * rate_cents_per_kwh;
    return (product + 500) / 1000;
}

Result calculate_settlement(const Input& input) {
    const int parking = calculate_parking_fee(input);
    const long long imported = calculate_energy_amount(
        input.import_wh, input.import_rate_cents_per_kwh);
    const long long exported = calculate_energy_amount(
        input.export_wh, input.export_rate_cents_per_kwh);
    return {parking, imported, exported, parking + imported - exported};
}

Input parse_arguments(int argc, char* argv[]) {
    if (argc != 12) {
        throw std::invalid_argument("expected 11 arguments");
    }
    return {
        std::stoi(argv[1]), argv[2], std::stoi(argv[3]), std::stoi(argv[4]),
        std::stoi(argv[5]), std::stoi(argv[6]), std::stoi(argv[7]) != 0,
        std::stoi(argv[8]) != 0, std::stoi(argv[9]) != 0,
        std::stoi(argv[10]), std::stoi(argv[11])
    };
}

int main(int argc, char* argv[]) {
    try {
        const Input input = parse_arguments(argc, argv);
        validate(input);
        const Result result = calculate_settlement(input);
        const std::string settlement = result.net_amount_cents < 0 ? "CREDIT" :
            (result.net_amount_cents > 0 ? "PAY" : "ZERO");
        std::cout << "{\"status\":\"ok\",\"parking_fee_cents\":"
                  << result.parking_fee_cents << ",\"import_cost_cents\":"
                  << result.import_cost_cents << ",\"export_credit_cents\":"
                  << result.export_credit_cents << ",\"net_amount_cents\":"
                  << result.net_amount_cents << ",\"settlement\":\""
                  << settlement << "\"}" << std::endl;
        return 0;
    } catch (const std::exception& error) {
        std::cout << "{\"status\":\"error\",\"error\":\""
                  << error.what() << "\"}" << std::endl;
        return 2;
    }
}
