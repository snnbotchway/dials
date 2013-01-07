
#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include "../from_hkl_to_detector.h"

using namespace boost::python;
using namespace dials::geometry::transform;

namespace dials { namespace geometry { namespace transform { 
    
namespace boost_python {

void export_from_hkl_to_detector() 
{
    class_ <from_hkl_to_detector> ("from_hkl_to_detector")
        .def(init <from_hkl_to_beam_vector, 
                   from_beam_vector_to_detector > ((
                arg("hkl_to_s1"), 
                arg("s1_to_xy"))))          
        .def("apply", 
            &from_hkl_to_detector::apply, (
                arg("hkl"), 
                arg("phi")));
}

}

}}}
