# Developed by: David Bailey
# ArcGIS Version: 10.3.1
# Description: This script creates Domains in an ESRI Geodatabase from Look Up tables in an Oracle Database

#################################

# Import arcpy site-package, os
import arcpy
import os

# Set geoprocessing environment / Oracle Database connection

### This needs to be the connection file to the Oracle SDE database GISDB2  ###
aWS = r"C:\Users\username\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\Connection to GISDatabase.sde"
arcpy.env.workspace = aWS


try:

    # Create empty dictionaries to hold Look Up tables and ESRI Domains
    LuDict = {} # lookup dictionary
    GisDict = {} # esri dictionary

    ### Move Oracle Lookup tables into ESRI domains ###

    # List all Look Up tables in Oracle Database
    luList = set(arcpy.ListTables("*LKS") + arcpy.ListTables("*_LK")) # lookup tables in this particular DB instance are prefixed with LKS and _LK

    print "processing..."

    # Create a list of table names where if these are detected then they will be migrated into ESRI domains using CreateDomain_management function
    removeList = []

    # loop through all look up tables in DB
    for lu in luList:

        # List all fields in the current table
        fieldsInTable = arcpy.ListFields(lu)

        # Create variable for the second field in the current table
        # The second field is the field in the database table from which to derive domain code values (NOTE: this may change depending on your table structure)
        secondField = fieldsInTable[1].name

        ## This needs to be the connection file to the new Production Database where new ESRI domains will reside ##
        dWorkspace = r"C:\Users\username\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\Connection to GIS_PROD_SDE.sde"

        # If the Look Up table is in the removeList then migrate into ESRI domains using CreateDomain_management function

        # If not then continue on down the For Loop and migrate look up tables

        #  Add removeList tables separately because they have no DESCRIPTION field
        if lu in removeList:

            # Get Oracle Lookup Table Values and add to LookUp Table dictionary - using List Comprehension
            lu_dom = [row.getValue(secondField) for row in arcpy.SearchCursor(lu)]
            LuDict[lu] = lu_dom

            # Get ESRI Coded Domain Values and add to ESRI Domain dictionary - using List Comprehension
            GisDict = {domain.name: domain.codedValues.keys() for domain in
                       arcpy.da.ListDomains(dWorkspace) if
                       domain.domainType == 'CodedValue'}

            # if/then statement to check if Look Up table is in ESRI Domain dictionary
            if lu in GisDict:

               print "Domains already exist"

            # tables are in removeList and not in GisDict
            else:

                print "Add New Domain"

                # Create Domain for removeList tables
                arcpy.CreateDomain_management(dWorkspace, lu, secondField, "TEXT", "CODED", "", "")

                fieldsInFC = arcpy.ListFields(lu)
                secondField = fieldsInFC[1].name

                # Get Oracle Lookup Table Values and add to LookUp Table dictionary
                lu_dom = [row.getValue(secondField) for row in arcpy.SearchCursor(lu)]
                LuDict[lu] = lu_dom

                # loop through all Look Up table Values in the associated Look Up table
                for lu_value in LuDict[lu]:
                    print lu_value
                    print "Adding " + lu_value + " to Domain"
                    arcpy.AddCodedValueToDomain_management(dWorkspace, lu, lu_value, lu_value)


        # migrate look up tables to ESRI domains
        else:

            # Set geoprocessing environment / Oracle Database connection
            ### This needs to be the connection file to the Oracle SDE database GISDB2  ###
            aWS = r"C:\Users\username\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\Connection to GISDatabase.sde"
            arcpy.env.workspace = aWS

            ### Migrate Look up values to ESRI domains

            # List all fields in the current table
            fieldsInTable = arcpy.ListFields(lu)
            # Create variable for the second field in the current table
            secondField = fieldsInTable[1].name

            # Create variable for the DESCRIPTION field
            Desc = "DESCRIPTION"

            # Geodatabase that will house the domains
            ## This needs to be the connection file to the new Production Database ##
            dWorkspace = r"C:\Users\username\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\Connection to GIS_PROD_SDE.sde"

            print "processing:" + lu + "..."

            # Create list that holds all ESRI domain names in ESRI geodatabase
            desc1 = arcpy.Describe(dWorkspace)
            doms1 = desc1.Domains

            # If LookUpTable Name exists in ESRI domain names then check if there are new Look Up table values
            if lu in doms1:

                print "Domains aleady exist"

            # If LookUpTable Name does not exist in ESRI domain names

            else:

                # A list that holds all fields that have a SHORT INT data type
                intList = []

                # If not in the FLOAT and INT lists
                if lu not in intList:

                    print "DOUBLE - " + lu

                    # Convert the specific Oracle LookUp table to an ESRI domain
                    arcpy.TableToDomain_management(lu, secondField, Desc, dWorkspace, lu, "", "REPLACE")

                # If in INT lists
                else:

                    # Manually add Domain if Table field is a SHORT INT
                    for int2 in intList:

                        if int2 == lu:

                            print "Short Int: " + lu

                            # Create Domain
                            arcpy.CreateDomain_management(dWorkspace2, lu, Desc2, "SHORT", "CODED")

                            # List all fields in the current table
                            fieldsInTable = arcpy.ListFields(lu)
                            # Create variable for the second field in the current table
                            fieldname = fieldsInTable[1].name
                            # Create variable for the third (Description) field in the current table
                            descname = fieldsInTable[2].name
                            values = arcpy.SearchCursor(lu)

                            # Create a list to hold all coded values
                            cd1 = []
                            # Create a list to hold all Descriptions
                            desclist1 = []

                            # Loop through all fields in a table
                            for value in values:
                                # Get values (second field in table)
                                sizes = value.getValue(fieldname)
                                # Recast data type for sizes to FLOAT
                                ints = int(sizes)

                                # Get values for the DESCRIPTION field (third field in table)
                                descs = value.getValue(descname)

                                # Append SIZE values to list
                                cd1.append(ints)
                                # Append DESCRIPTION values to list
                                desclist1.append(descs)

                                # Loop through Coded Value list and Description list

                                # Loop through Coded Value list and Description list
                                for (code, code2) in zip(cd1, desclist1):
                                    # Added coded values to domain
                                    print "add domains"
                                    arcpy.AddCodedValueToDomain_management(dWorkspace2, lu, code, code2)



    # Remove all 0's and TBD's coded domain values (NOTE: this may not be applicable with your data)

    # List all domains in Geodatabase
    domains = arcpy.da.ListDomains(r"C:\Users\username\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\Connection to GIS_PROD_SDE.sde")

    # Check for 0's and TBD's coded domain values and remove them
    for dom in domains:
        if dom.domainType == 'CodedValue':
            coded_values = dom.codedValues
            for code in coded_values:
                dWorkspace3 = r"C:\Users\bailey\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\Connection to SJGISDB SDE.sde"
                if code == "TBD":
                    print "TBD value is being removed from " + dom.name
                    arcpy.DeleteCodedValueFromDomain_management(dWorkspace3, dom.name, code)
                elif code == 0.0:
                    print "0 value is being removed from " + dom.name
                    arcpy.DeleteCodedValueFromDomain_management(dWorkspace3, dom.name, code)
                else:
                    print "No TBD or 0 values found in " + dom.name

        else:
            print dom.name

    del dom
    del domains

except:

    # Code to run when an error occured
    print "\nAn ERROR Occurred!"
    print "\n" + arcpy.GetMessages() + "\n"


else:

    # Message when there was no error
    print "\nThere were no errors\n"
    # Message when there was no error
    print "\nScript is complete"
