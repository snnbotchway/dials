
#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include "../from_beam_vector_to_detector.h"

using namespace boost::python;
using namespace dials::geometry::transform;

namespace dials { namespace geometry { namespace transform { 
    
namespace boost_python {

void export_from_beam_vector_to_detector() 
{
    class_ <from_beam_vector_to_detector> ("from_beam_vector_to_detector")
        .def(init <detector_coordinate_system, 
                   scitbx::vec2 <double>,
                   double> ((
                arg("dcs"), 
                arg("origin"), 
                arg("distance"))))
        .def("apply", 
            &from_beam_vector_to_detector::apply, (
                arg("s1")));
}

}

}}}
