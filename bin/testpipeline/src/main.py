from checks.plane_check import assign_datum_planes_to_layer
from checks.sketch_check import assign_sketches_to_layer
from utils.save_part import save_active_part
from checks.solidbody_check import assign_holes_to_layer
from checks.buypart_check import check_is_buy_part

def main():
    #  Check and correct layers if necessary
    assign_datum_planes_to_layer()
    assign_sketches_to_layer()
    #assign_holes_to_layer()
    check_is_buy_part()
    save_active_part()

if __name__ == '__main__':
    main()

